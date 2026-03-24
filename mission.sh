#!/usr/bin/env bash
set -euo pipefail

# ─── Grid Mission Control ───────────────────────────────────────────────────
# Research and execution harness for Claude Code + Obsidian
# ─────────────────────────────────────────────────────────────────────────────

GRID_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MISSION_DIR="$GRID_DIR/.mission"
KNOWLEDGE_DIR="$GRID_DIR/knowledge"
STATE_FILE="$MISSION_DIR/state.json"
LOGS_DIR="$MISSION_DIR/logs"
MODELS_CONF="$MISSION_DIR/models.conf"
DECISION_LOG="$KNOWLEDGE_DIR/decision-log.md"
EXAMPLES_DIR="$GRID_DIR/examples"
ROUTING_LOG="$MISSION_DIR/routing-log.jsonl"

# ─── Verification helpers ─────────────────────────────────────────────────────
VERIFICATION_CONF="$MISSION_DIR/verification.conf"

verification_enabled() {
    # Returns 0 (true) if verification is enabled, 1 (false) otherwise
    [[ -f "$VERIFICATION_CONF" ]] || return 1
    local val
    val="$(grep '^enabled=' "$VERIFICATION_CONF" | head -1 | cut -d= -f2 | tr -d '[:space:]')"
    [[ "$val" == "true" || "$val" == "1" || "$val" == "yes" ]]
}

verification_model() {
    # Returns the verification model name (empty string = use default)
    [[ -f "$VERIFICATION_CONF" ]] || return 0
    grep '^model=' "$VERIFICATION_CONF" | head -1 | cut -d= -f2 | tr -d '[:space:]'
}

verification_fail_action() {
    # Returns: warn | block | retry
    [[ -f "$VERIFICATION_CONF" ]] || { echo "warn"; return 0; }
    local val
    val="$(grep '^fail_action=' "$VERIFICATION_CONF" | head -1 | cut -d= -f2 | tr -d '[:space:]')"
    echo "${val:-warn}"
}

# ─── Routing ─────────────────────────────────────────────────────────────────
ROUTE_OVERRIDE=""  # set via --route-override flag

# ─── Dory mode (ephemeral — don't save anything to files) ────────────────────
DORY_MODE="${DORY_MODE:-0}"  # set via --dory flag or env

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ─── Ensure directories exist ───────────────────────────────────────────────
ensure_dirs() {
    mkdir -p "$MISSION_DIR" "$LOGS_DIR" "$KNOWLEDGE_DIR/execplans" \
             "$KNOWLEDGE_DIR/missions" "$KNOWLEDGE_DIR/templates"
    [[ -f "$STATE_FILE" ]] || echo '{}' > "$STATE_FILE"
    [[ -f "$DECISION_LOG" ]] || printf '# Decision Log\n\n> Append-only log of non-routine events across all missions.\n> Format: timestamp | mission | task | event | link\n\n' > "$DECISION_LOG"
}

# ─── Graceful shutdown ───────────────────────────────────────────────────────
cleanup() {
    printf "\n${YELLOW}⚠ Interrupted. State saved.${RESET}\n"
    exit 130
}
trap cleanup INT TERM

# ─── Utility functions ───────────────────────────────────────────────────────
timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//'
}

elapsed_since() {
    local start=$1
    local now
    now=$(date +%s)
    local diff=$((now - start))
    printf '%dm%ds' $((diff / 60)) $((diff % 60))
}

safe_write() {
    local dest="$1"
    local content="$2"
    # Dory mode: skip all file writes (except state.json which is needed for TUI)
    if [[ "${DORY_MODE:-0}" == "1" && "$dest" != *"state.json"* ]]; then
        return 0
    fi
    local dir
    dir="$(dirname "$dest")"
    mkdir -p "$dir"
    local tmp
    tmp="$(mktemp "$dir/.tmp.XXXXXX")"
    printf '%s' "$content" > "$tmp"
    mv "$tmp" "$dest"
}

# ─── State management ───────────────────────────────────────────────────────
get_state() {
    local mission="$1" task_id="$2"
    jq -r --arg m "$mission" --arg t "$task_id" '.[$m][$t] // "pending"' "$STATE_FILE"
}

set_state() {
    local mission="$1" task_id="$2" status="$3"
    local tmp
    tmp="$(mktemp "$MISSION_DIR/.tmp.XXXXXX")"
    jq --arg m "$mission" --arg t "$task_id" --arg s "$status" \
       '.[$m] = (.[$m] // {} | .[$t] = $s)' "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
}

# ─── Model resolution ───────────────────────────────────────────────────────
ACTIVE_MODEL=""
ACTIVE_MODEL_NAME=""

load_models() {
    # models.conf is read directly via grep — no associative arrays needed
    :
}

get_model_cmd() {
    local name="$1"
    if [[ -f "$MODELS_CONF" ]]; then
        local line
        line="$(grep "^${name}=" "$MODELS_CONF" | head -1)" || true
        if [[ -n "$line" ]]; then
            echo "${line#*=}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
            return 0
        fi
    fi
    return 1
}

list_model_names() {
    if [[ -f "$MODELS_CONF" ]]; then
        grep -v '^#' "$MODELS_CONF" | grep -v '^[[:space:]]*$' | cut -d= -f1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^router$'
    fi
}

resolve_model() {
    local flag_model="${1:-}"
    local model_name=""

    if [[ -n "$flag_model" ]]; then
        model_name="$flag_model"
    elif [[ -n "${MODEL:-}" ]]; then
        model_name="$MODEL"
    else
        model_name="auto"
    fi

    # 'auto' is a virtual model — routing happens per-task in execute_task
    if [[ "$model_name" == "auto" ]]; then
        ACTIVE_MODEL="__auto__"
        ACTIVE_MODEL_NAME="auto"
        return 0
    fi

    local cmd
    cmd="$(get_model_cmd "$model_name")" || true
    if [[ -z "$cmd" ]]; then
        printf "${RED}✗ Unknown model: %s${RESET}\n" "$model_name" >&2
        printf "  Available models: auto, %s\n" "$(list_model_names | tr '\n' ', ')" >&2
        exit 1
    fi

    ACTIVE_MODEL="$cmd"
    ACTIVE_MODEL_NAME="$model_name"
}

# ─── File context for non-Claude models ──────────────────────────────────────
CONTEXT_DIRS_CONF="$MISSION_DIR/context-dirs.conf"

build_file_context() {
    local prompt="$1"
    # Only inject for non-Claude models (Claude has its own file tools)
    local model_name="${2:-}"
    if [[ "$model_name" == "claude" ]]; then
        echo "$prompt"
        return 0
    fi

    # Read context directories from config (one dir per line)
    local context_dirs=()
    if [[ -f "$CONTEXT_DIRS_CONF" ]]; then
        while IFS= read -r dir; do
            [[ -z "$dir" || "$dir" == \#* ]] && continue
            dir="$(eval echo "$dir")"  # expand ~ and $HOME
            [[ -d "$dir" ]] && context_dirs+=("$dir")
        done < "$CONTEXT_DIRS_CONF"
    fi

    # Default: include Grid knowledge dir
    if [[ ${#context_dirs[@]} -eq 0 ]]; then
        context_dirs=("$KNOWLEDGE_DIR")
    fi

    # Build file listing (shallow — just names and sizes, not contents)
    local file_context=""
    for dir in "${context_dirs[@]}"; do
        local listing
        listing="$(find "$dir" -maxdepth 2 -type f \( -name '*.md' -o -name '*.txt' -o -name '*.json' -o -name '*.py' -o -name '*.sh' \) -exec ls -lh {} \; 2>/dev/null | awk '{print $NF, $5}' | head -50)" || true
        if [[ -n "$listing" ]]; then
            file_context="${file_context}
[Files in ${dir}]:
${listing}
"
        fi
    done

    # Also list top-level Documents directory
    local docs_dir="$HOME/Documents"
    if [[ -d "$docs_dir" ]]; then
        local docs_listing
        docs_listing="$(ls -1 "$docs_dir" 2>/dev/null | head -30)" || true
        if [[ -n "$docs_listing" ]]; then
            file_context="${file_context}
[Folders in ~/Documents]:
${docs_listing}
"
        fi
    fi

    if [[ -n "$file_context" ]]; then
        printf 'You ARE able to see the user'\''s local files. The following is a real listing of their filesystem. Use this information to answer their question accurately. Do NOT say you cannot access files — you can see them below.\n\n%s\n\n---\nUser question: %s' "$file_context" "$prompt"
    else
        echo "$prompt"
    fi
}

# ─── Runner ──────────────────────────────────────────────────────────────────
run_prompt() {
    local prompt="$1"
    local log_file="$2"
    local model_cmd="${3:-$ACTIVE_MODEL}"
    local model_name="${4:-$ACTIVE_MODEL_NAME}"

    # 'auto' at run_prompt level means routing wasn't done — fall back
    # (route_task handles auto for missions; this fallback covers ask/plan/review)
    if [[ "$model_name" == "auto" || "$model_cmd" == "__auto__" ]]; then
        # Try local MLX model first, fall back to claude
        local local_cmd
        local_cmd="$(get_model_cmd "local" 2>/dev/null)" || true
        if [[ -n "$local_cmd" ]]; then
            model_name="local"
            model_cmd="$local_cmd"
        else
            model_name="claude"
            model_cmd="$(get_model_cmd "claude")"
        fi
    fi

    # Inject file context for non-Claude models
    if [[ "$model_name" != "claude" ]]; then
        prompt="$(build_file_context "$prompt" "$model_name")"
    fi

    # Execute with fallback: if model fails and isn't local, try local as fallback
    local run_status=0
    if [[ "$model_name" == "local-api" || "$model_name" == "ldr" ]]; then
        local json_payload
        json_payload=$(jq -n --arg p "$prompt" '{"model":"default","messages":[{"role":"user","content":$p}]}')
        eval "$model_cmd" "'$json_payload'" > "$log_file" 2>&1 || run_status=$?
    elif [[ "$model_name" == "local" || "$model_name" == "local-8b" || "$model_name" == "ollama" || "$model_name" == "deepseek" ]]; then
        # MLX / ollama — pipe prompt via stdin
        printf '%s' "$prompt" | eval "$model_cmd" > "$log_file" 2>&1 || run_status=$?
    else
        # Other models (claude, openai, etc.) — pipe prompt via stdin
        local stderr_file
        stderr_file="$(mktemp)"
        printf '%s' "$prompt" | eval "$model_cmd" > "$log_file" 2>"$stderr_file" || run_status=$?

        # If output is empty but exit was 0, retry once (claude can silently produce nothing)
        if [[ $run_status -eq 0 && ! -s "$log_file" ]]; then
            printf "  ${DIM}⟳ Empty output, retrying...${RESET}\n" >&2
            printf '%s' "$prompt" | eval "$model_cmd" > "$log_file" 2>"$stderr_file" || run_status=$?
        fi

        # If still empty or failed, append stderr to log for diagnosis
        if [[ ! -s "$log_file" && -s "$stderr_file" ]]; then
            cat "$stderr_file" >> "$log_file"
        fi
        rm -f "$stderr_file"

        # If non-local model failed or produced empty output, try local as fallback
        if [[ ($run_status -ne 0 || ! -s "$log_file") && "$model_name" != "local" ]]; then
            local local_cmd
            local_cmd="$(get_model_cmd "local" 2>/dev/null)" || true
            if [[ -n "$local_cmd" ]]; then
                printf '\n[%s failed, falling back to local]\n' "$model_name" >> "$log_file"
                printf '%s' "$prompt" | eval "$local_cmd" >> "$log_file" 2>&1
                run_status=$?
            fi
        fi
    fi

    return $run_status
}

# ─── Decision log ────────────────────────────────────────────────────────────
log_decision() {
    local mission="$1" task_id="$2" event="$3"
    local entry
    entry="| $(timestamp) | $mission | $task_id | $event | [[missions/$mission/$task_id]] |"
    printf '\n%s' "$entry" >> "$DECISION_LOG"
}

# ─── Routing ─────────────────────────────────────────────────────────────────

check_backend_available() {
    local backend="$1"
    case "$backend" in
        local)
            local local_cmd
            local_cmd="$(get_model_cmd "local" 2>/dev/null)" || return 1
            [[ -n "$local_cmd" ]] && return 0
            return 1
            ;;
        claude)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

ROUTER_SYSTEM_PROMPT='Choose which backend to use. Reply with ONLY valid JSON.

Example for claude: {"backend":"claude","reasoning":"needs web search"}
Example for local: {"backend":"local","reasoning":"simple summary task"}

Rules:
- "claude" for: research, web search, complex code, architecture, debugging, multi-file changes
- "local" for: simple questions, formatting, summarization, boilerplate, short answers

Prefer "local" when possible. Use "claude" only when genuinely needed.'

route_task() {
    local task_type="$1" prompt_text="$2" expected="$3"

    local router_cmd
    router_cmd="$(get_model_cmd "router" 2>/dev/null)" || router_cmd=""

    if [[ -n "$router_cmd" ]]; then
        # Try ML router first
        local user_msg="${ROUTER_SYSTEM_PROMPT}

Task type: ${task_type}
Prompt: ${prompt_text:0:300}"

        local content
        content="$(printf '%s' "$user_msg" | eval "$router_cmd" 2>/dev/null)" || content=""

        # Extract backend — look for "claude" or "local" in output
        local backend=""
        local reasoning=""
        if echo "$content" | grep -q '"backend"'; then
            backend="$(echo "$content" | python3 -c "
import sys, json, re
text = sys.stdin.read()
# Find any JSON-like object
m = re.search(r'\{[^}]*\"backend\"\s*:\s*\"(claude|local)\"[^}]*\}', text)
if m:
    # Extract just the backend value
    b = re.search(r'\"backend\"\s*:\s*\"(claude|local)\"', m.group())
    if b: print(b.group(1))
" 2>/dev/null)" || backend=""
            reasoning="$(echo "$content" | python3 -c "
import sys, re
text = sys.stdin.read()
m = re.search(r'\"reasoning\"\s*:\s*\"([^\"]+)\"', text)
if m: print(m.group(1))
" 2>/dev/null)" || reasoning=""
        fi

        # If ML router gave a valid answer, use it
        if [[ "$backend" == "claude" || "$backend" == "local" ]]; then
            # Availability check
            if [[ "$backend" == "local" ]] && ! check_backend_available local; then
                reasoning="[local unavailable, fell back] $reasoning"
                backend="claude"
            fi
            echo "${backend}|${reasoning}"
            return 0
        fi
        # ML router failed — fall through to rule-based
    fi

    # Rule-based fallback
    local backend="claude"
    local reasoning="rule-based"
    local prompt_lower
    prompt_lower="$(printf '%s' "${prompt_text:0:500}" | tr '[:upper:]' '[:lower:]')"

    # These types always need claude
    if [[ "$task_type" == "research" || "$task_type" == "gap-analysis" ]]; then
        backend="claude"
        reasoning="$task_type needs web search/deep analysis"
    elif [[ "$prompt_lower" == *"search"* || "$prompt_lower" == *"investigate"* || \
            "$prompt_lower" == *"refactor"* || "$prompt_lower" == *"implement"* || \
            "$prompt_lower" == *"debug"* || "$prompt_lower" == *"architect"* ]]; then
        backend="claude"
        reasoning="complex task keywords detected"
    elif check_backend_available local; then
        backend="local"
        reasoning="simple task, local can handle"
    fi

    echo "${backend}|${reasoning}"
}

append_routing_log() {
    local task_id="$1" mission="$2" prompt_preview="$3" routed_to="$4" \
          reasoning="$5" task_type="$6" outcome="$7"
    local entry
    entry="$(jq -n \
        --arg ts  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --arg tid "$task_id" \
        --arg m   "$mission" \
        --arg pp  "$prompt_preview" \
        --arg rt  "$routed_to" \
        --arg r   "$reasoning" \
        --arg tt  "$task_type" \
        --arg o   "$outcome" \
        '{timestamp:$ts,task_id:$tid,mission:$m,prompt_preview:$pp,routed_to:$rt,reasoning:$r,task_type:$tt,outcome:$o}')"
    echo "$entry" >> "$ROUTING_LOG"
}

# ─── Obsidian note writing ───────────────────────────────────────────────────
write_task_note() {
    local mission="$1" task_id="$2" task_name="$3" milestone="$4" \
          task_type="$5" status="$6" expected="$7" prompt_text="$8" \
          output="$9" validation_result="${10}" model="${11}" \
          router_decision="${12:-}" router_reasoning="${13:-}"

    local note_dir="$KNOWLEDGE_DIR/missions/$mission"
    local note_path="$note_dir/$task_id.md"
    mkdir -p "$note_dir"

    # Preserve existing My Notes content
    local my_notes=""
    if [[ -f "$note_path" ]]; then
        my_notes="$(awk '/^## My Notes/{found=1; next} found' "$note_path" | sed '/^<!-- Write below/d')"
    fi

    # Determine tags and confidence
    local tag="#implementation"
    local confidence="high"
    case "$task_type" in
        research)   tag="#research"; confidence="medium" ;;
        synthesis)  tag="#synthesis"; confidence="medium" ;;
        gap-analysis) tag="#research"; confidence="low" ;;
    esac

    local router_fm=""
    if [[ -n "$router_decision" ]]; then
        router_fm="router_decision: $router_decision
router_reasoning: '$(printf '%s' "$router_reasoning" | sed "s/'/''/g")'"
    fi

    local content
    content="$(cat <<NOTEEOF
---
status: $status
milestone: $(printf '%s' "$milestone")
date: $(date '+%Y-%m-%d')
type: $task_type
model: $model
tags: [$tag]
confidence: $confidence
$(printf '%s' "$router_fm")
---

## Task Description

$(printf '%s' "$prompt_text")

## Expected Behavior

$(printf '%s' "$expected")

## Findings / Output

$(printf '%s' "$output")

## Validation Result

$(printf '%s' "$validation_result")

## My Notes
<!-- Write below this line. The harness reads this on re-run. Use #redo to re-run this task, #skip to skip it, #pivot:<new direction> to change the approach. -->
$my_notes
NOTEEOF
)"
    safe_write "$note_path" "$content"
}

write_mission_index() {
    local mission="$1" mission_file="$2"
    local index_dir="$KNOWLEDGE_DIR/missions/$mission"
    local index_path="$index_dir/_index.md"
    mkdir -p "$index_dir"

    if [[ ! -f "$mission_file" ]]; then
        return 0
    fi

    local total completed failed skipped pending
    total="$(jq '.tasks | length' "$mission_file" 2>/dev/null)" || total=0
    completed="$(jq -r --arg m "$mission" '.[$m] // {} | to_entries | map(select(.value == "completed")) | length' "$STATE_FILE")"
    failed="$(jq -r --arg m "$mission" '.[$m] // {} | to_entries | map(select(.value == "failed")) | length' "$STATE_FILE")"
    skipped="$(jq -r --arg m "$mission" '.[$m] // {} | to_entries | map(select(.value == "skipped")) | length' "$STATE_FILE")"
    pending=$((total - completed - failed - skipped))

    local content
    content="---
mission: $mission
date: $(date '+%Y-%m-%d')
total: $total
completed: $completed
failed: $failed
skipped: $skipped
pending: $pending
---

# Mission: $mission

**Total:** $total | **Completed:** $completed | **Failed:** $failed | **Skipped:** $skipped | **Pending:** $pending

## Tasks

| ID | Name | Status | Type | Model | Note |
|----|------|--------|------|-------|------|"

    local task_ids task_id t_name t_type t_status
    task_ids="$(jq -r '.tasks[].id' "$mission_file")"
    while IFS= read -r task_id; do
        t_name="$(jq -r --arg id "$task_id" '.tasks[] | select(.id == $id) | .name' "$mission_file")"
        t_type="$(jq -r --arg id "$task_id" '.tasks[] | select(.id == $id) | .type // "code"' "$mission_file")"
        t_status="$(get_state "$mission" "$task_id")"
        content="$content
| $task_id | $(printf '%s' "$t_name" | sed 's/|/\\|/g') | $t_status | $t_type | $ACTIVE_MODEL_NAME | [[$mission/$task_id]] |"
    done <<< "$task_ids"

    safe_write "$index_path" "$content"
}

# ─── Read feedback and notes ────────────────────────────────────────────────
read_my_notes() {
    local note_path="$1"
    [[ -f "$note_path" ]] || return 0
    local notes
    notes="$(awk '/^## My Notes/{found=1; next} found' "$note_path" | sed '/^<!-- Write below/d')"
    notes="$(echo "$notes" | sed '/^[[:space:]]*$/d')"
    echo "$notes"
}

read_feedback() {
    local mission="$1"
    local fb_path="$KNOWLEDGE_DIR/missions/$mission/_feedback.md"
    [[ -f "$fb_path" ]] || return 0
    local content
    content="$(cat "$fb_path" | sed '/^[[:space:]]*$/d')"
    echo "$content"
}

check_directives() {
    local notes="$1"
    # Returns: redo, skip, pivot:<text>, or empty
    if echo "$notes" | grep -q '#redo'; then
        echo "redo"
    elif echo "$notes" | grep -q '#skip'; then
        echo "skip"
    elif echo "$notes" | grep -qo '#pivot:.*'; then
        echo "$notes" | grep -o '#pivot:.*' | head -1 | sed 's/#pivot://'
    fi
}

# ─── Task execution ─────────────────────────────────────────────────────────
execute_task() {
    local mission="$1" mission_file="$2" task_json="$3" task_index="$4" task_total="$5"

    local task_id task_name milestone expected prompt_text validation task_type preconditions
    task_id="$(echo "$task_json" | jq -r '.id')"
    task_name="$(echo "$task_json" | jq -r '.name')"
    milestone="$(echo "$task_json" | jq -r '.milestone // ""')"
    expected="$(echo "$task_json" | jq -r '.expected // ""')"
    prompt_text="$(echo "$task_json" | jq -r '.prompt')"
    validation="$(echo "$task_json" | jq -r '.validation // ""')"
    task_type="$(echo "$task_json" | jq -r '.type // "code"')"
    preconditions="$(echo "$task_json" | jq -r '.preconditions // [] | .[]')"

    local task_start
    task_start=$(date +%s)

    # Check current state
    local current_state
    current_state="$(get_state "$mission" "$task_id")"

    # Check for directives in existing notes
    local note_path="$KNOWLEDGE_DIR/missions/$mission/$task_id.md"
    local my_notes=""
    my_notes="$(read_my_notes "$note_path")"

    if [[ -n "$my_notes" ]]; then
        local directive
        directive="$(check_directives "$my_notes")"
        if [[ "$directive" == "redo" ]]; then
            printf "${YELLOW}↻ %s — #redo directive found, re-running${RESET}\n" "$task_id"
            set_state "$mission" "$task_id" "pending"
            current_state="pending"
        elif [[ "$directive" == "skip" ]]; then
            printf "${DIM}⊘ %s — #skip directive found${RESET}\n" "$task_id"
            set_state "$mission" "$task_id" "skipped"
            return 0
        elif [[ -n "$directive" ]]; then
            # pivot
            printf "${CYAN}⟳ %s — #pivot directive found${RESET}\n" "$task_id"
            prompt_text="$directive"
            set_state "$mission" "$task_id" "pending"
            current_state="pending"
        fi
    fi

    # Skip if completed
    if [[ "$current_state" == "completed" || "$current_state" == "skipped" ]]; then
        printf "${DIM}⊘ [%d/%d] %s — %s (already %s)${RESET}\n" "$task_index" "$task_total" "$task_id" "$task_name" "$current_state"
        return 0
    fi

    # Check preconditions
    if [[ -n "$preconditions" ]]; then
        while IFS= read -r dep; do
            [[ -z "$dep" ]] && continue
            local dep_state
            dep_state="$(get_state "$mission" "$dep")"
            if [[ "$dep_state" != "completed" ]]; then
                printf "${YELLOW}⏸ [%d/%d] %s — blocked on %s (%s)${RESET}\n" "$task_index" "$task_total" "$task_id" "$dep" "$dep_state"
                log_decision "$mission" "$task_id" "Blocked: precondition $dep is $dep_state"
                return 0
            fi
        done <<< "$preconditions"
    fi

    # ── Resolve effective backend (routing or explicit) ───────────────────────
    local task_model_name task_model_cmd router_decision="" router_reasoning=""
    if [[ -n "$ROUTE_OVERRIDE" ]]; then
        # --route-override forces a specific backend, skip router entirely
        task_model_name="$ROUTE_OVERRIDE"
        task_model_cmd="$(get_model_cmd "$task_model_name")" || task_model_cmd=""
        if [[ -z "$task_model_cmd" ]]; then
            printf "${RED}✗ Unknown route-override backend: %s${RESET}\n" "$task_model_name" >&2
            exit 1
        fi
        router_decision="$task_model_name"
        router_reasoning="Forced via --route-override"
    elif [[ "$ACTIVE_MODEL_NAME" == "auto" ]]; then
        printf "  ${DIM}Routing task...${RESET}\n"
        local route_result
        route_result="$(route_task "$task_type" "$prompt_text" "$expected")"
        router_decision="${route_result%%|*}"
        router_reasoning="${route_result#*|}"
        task_model_name="$router_decision"
        task_model_cmd="$(get_model_cmd "$task_model_name")" || task_model_cmd=""
        if [[ -z "$task_model_cmd" ]]; then
            printf "  ${YELLOW}⚠ No cmd for routed backend '%s', falling back to claude${RESET}\n" "$task_model_name" >&2
            task_model_name="claude"
            task_model_cmd="$(get_model_cmd "claude")"
            router_reasoning="[no cmd for $router_decision, fell back] $router_reasoning"
            router_decision="claude"
        fi
        printf "  ${CYAN}⟶ Routed to: %s${RESET} ${DIM}(%s)${RESET}\n" "$task_model_name" "$router_reasoning"
    else
        task_model_name="$ACTIVE_MODEL_NAME"
        task_model_cmd="$ACTIVE_MODEL"
    fi

    # Print status
    printf "${BOLD}${CYAN}▸ [%d/%d] %s${RESET} — %s\n" "$task_index" "$task_total" "$task_id" "$task_name"
    [[ -n "$milestone" ]] && printf "  ${DIM}Milestone: %s${RESET}\n" "$milestone"
    [[ -n "$expected" ]] && printf "  ${DIM}Expected: %s${RESET}\n" "$expected"

    set_state "$mission" "$task_id" "running"

    # Build the full prompt
    local full_prompt=""

    # Prepend persistent memory
    local mem_ctx
    mem_ctx="$(load_memory_context)"
    if [[ -n "$mem_ctx" ]]; then
        full_prompt="Persistent context about the user:
$mem_ctx

"
    fi

    # Inject relevant knowledge base context for research/synthesis tasks
    if [[ "$task_type" == "research" || "$task_type" == "synthesis" || "$task_type" == "code" ]]; then
        local kb_ctx
        kb_ctx="$(load_relevant_context "$prompt_text" 2)"
        if [[ -n "$kb_ctx" ]]; then
            full_prompt="${full_prompt}${kb_ctx}"
        fi
    fi

    # Prepend global feedback
    local feedback
    feedback="$(read_feedback "$mission")"
    if [[ -n "$feedback" ]]; then
        full_prompt="${full_prompt}Global context from the researcher:
$feedback

"
    fi

    # Type-specific prompt augmentation
    case "$task_type" in
        research)
            full_prompt="$full_prompt$prompt_text

Search the web thoroughly. Cite all sources with URLs. Structure your findings clearly with evidence for and against. Output your complete findings as markdown directly to stdout. Do NOT create any files — just print your report."
            ;;
        synthesis)
            local source_content=""
            # Read all completed task outputs
            local completed_ids
            completed_ids="$(jq -r --arg m "$mission" '.[$m] // {} | to_entries | map(select(.value == "completed")) | .[].key' "$STATE_FILE")"
            while IFS= read -r cid; do
                [[ -z "$cid" ]] && continue
                local cfile="$KNOWLEDGE_DIR/missions/$mission/$cid.md"
                if [[ -f "$cfile" ]]; then
                    source_content="$source_content
--- Source: $cid ---
$(cat "$cfile")
"
                fi
            done <<< "$completed_ids"
            # Read additional sources
            local extra_sources
            extra_sources="$(echo "$task_json" | jq -r '.sources // [] | .[]')"
            while IFS= read -r src; do
                [[ -z "$src" ]] && continue
                if [[ -f "$src" ]]; then
                    source_content="$source_content
--- Source: $src ---
$(cat "$src")
"
                fi
            done <<< "$extra_sources"
            full_prompt="$full_prompt$prompt_text

Here are all the completed research findings:

$source_content

Synthesize these findings. Identify contradictions across sources. Extract key decisions needed. Produce a single coherent report."
            ;;
        gap-analysis)
            local synth_file="$KNOWLEDGE_DIR/missions/$mission/synthesis.md"
            local synth_content=""
            if [[ -f "$synth_file" ]]; then
                synth_content="$(cat "$synth_file")"
            fi
            full_prompt="$full_prompt$prompt_text

Here is the synthesis of findings so far:

$synth_content

Identify what's still unknown, what assumptions remain untested, what evidence is weak, and what the next research questions should be. Also output a follow-up mission as valid JSON with tasks array that could investigate these gaps."
            ;;
        *)
            full_prompt="$full_prompt$prompt_text"
            ;;
    esac

    # Append researcher notes if present
    if [[ -n "$my_notes" ]]; then
        # Strip directive lines
        local clean_notes
        clean_notes="$(echo "$my_notes" | grep -v '#redo\|#skip\|#pivot:' || true)"
        if [[ -n "$clean_notes" ]]; then
            full_prompt="$full_prompt

Additional context from the researcher: $clean_notes"
        fi
    fi

    # Execute
    local log_file="$LOGS_DIR/$task_id.log"
    printf "  ${DIM}Running with model: %s ...${RESET}\n" "$task_model_name"

    local run_status=0
    run_prompt "$full_prompt" "$log_file" "$task_model_cmd" "$task_model_name" || run_status=$?

    local output=""
    if [[ -f "$log_file" ]]; then
        output="$(cat "$log_file")"
    fi

    if [[ $run_status -ne 0 ]]; then
        printf "  ${RED}✗ Runner failed (exit %d)${RESET}\n" "$run_status"
        set_state "$mission" "$task_id" "failed"
        write_task_note "$mission" "$task_id" "$task_name" "$milestone" "$task_type" "failed" "$expected" "$prompt_text" "$output" "Runner failed with exit $run_status" "$task_model_name" "$router_decision" "$router_reasoning"
        log_decision "$mission" "$task_id" "Runner failed with exit $run_status"
        [[ -n "$router_decision" ]] && append_routing_log "$task_id" "$mission" "${prompt_text:0:100}" "$task_model_name" "$router_reasoning" "$task_type" "failed"
        return 0
    fi

    # Validation
    local val_result="No validation command"
    local val_status=0
    if [[ -n "$validation" && "$validation" != "null" ]]; then
        printf "  ${DIM}Validating...${RESET}\n"
        val_result="$(eval "$validation" 2>&1)" || val_status=$?
        if [[ $val_status -ne 0 ]]; then
            printf "  ${RED}✗ Validation failed (exit %d)${RESET}\n" "$val_status"
            set_state "$mission" "$task_id" "failed"
            write_task_note "$mission" "$task_id" "$task_name" "$milestone" "$task_type" "failed" "$expected" "$prompt_text" "$output" "Validation failed (exit $val_status): $val_result" "$task_model_name" "$router_decision" "$router_reasoning"
            log_decision "$mission" "$task_id" "Validation failed (exit $val_status)"
            [[ -n "$router_decision" ]] && append_routing_log "$task_id" "$mission" "${prompt_text:0:100}" "$task_model_name" "$router_reasoning" "$task_type" "failed"
            return 0
        fi
    elif [[ "$task_type" == "research" || "$task_type" == "gap-analysis" || "$task_type" == "synthesis" ]]; then
        # For research/synthesis/gap-analysis, validate that Claude produced substantial output
        if [[ ${#output} -lt 200 ]]; then
            printf "  ${RED}✗ Validation failed: output too short (%d chars)${RESET}\n" "${#output}"
            set_state "$mission" "$task_id" "failed"
            write_task_note "$mission" "$task_id" "$task_name" "$milestone" "$task_type" "failed" "$expected" "$prompt_text" "$output" "Output too short (${#output} chars — expected >200)" "$task_model_name" "$router_decision" "$router_reasoning"
            log_decision "$mission" "$task_id" "Validation failed: output too short"
            [[ -n "$router_decision" ]] && append_routing_log "$task_id" "$mission" "${prompt_text:0:100}" "$task_model_name" "$router_reasoning" "$task_type" "failed"
            return 0
        fi
        val_result="Output length: ${#output} chars"
    fi

    # ── DeepVerifier verification (opt-in via .mission/verification.conf) ──
    local verify_result="" verify_status=0 verify_feedback=""
    if [[ -f "$GRID_DIR/verify.py" ]] && verification_enabled; then
        printf "  ${DIM}Verifying output...${RESET}\n"
        local verify_model_flag=""
        local v_model
        v_model="$(verification_model)"
        [[ -n "$v_model" ]] && verify_model_flag="--model $v_model"

        verify_result="$(printf '%s' "$output" | python3 "$GRID_DIR/verify.py" \
            --task-id "$task_id" --mission "$mission" $verify_model_flag 2>&1)" || verify_status=$?

        # Parse verification JSON from stdout (last line)
        local verify_json
        verify_json="$(echo "$verify_result" | tail -1)"
        verify_feedback="$(echo "$verify_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('feedback','') or '')" 2>/dev/null)" || verify_feedback=""

        local verify_action
        verify_action="$(verification_fail_action)"

        if [[ $verify_status -eq 1 ]]; then
            # Verification failed — critical claims refuted
            printf "  ${RED}✗ Verification failed${RESET}\n"
            # Print stderr lines (human-readable summary)
            echo "$verify_result" | sed '$d' | while IFS= read -r vline; do
                [[ -n "$vline" ]] && printf "  ${DIM}%s${RESET}\n" "$vline"
            done

            if [[ "$verify_action" == "block" ]]; then
                set_state "$mission" "$task_id" "failed"
                write_task_note "$mission" "$task_id" "$task_name" "$milestone" "$task_type" "failed" "$expected" "$prompt_text" "$output" "Verification failed: $verify_feedback" "$task_model_name" "$router_decision" "$router_reasoning"
                log_decision "$mission" "$task_id" "Verification failed (blocked)"
                return 0
            elif [[ "$verify_action" == "retry" && -n "$verify_feedback" ]]; then
                printf "  ${YELLOW}↻ Retrying with verification feedback...${RESET}\n"
                full_prompt="$full_prompt

IMPORTANT CORRECTION from verification:
$verify_feedback

Please revise your output to address these issues."
                run_prompt "$full_prompt" "$log_file" "$task_model_cmd" "$task_model_name" || true
                [[ -f "$log_file" ]] && output="$(cat "$log_file")"
                val_result="$val_result | Verification retry applied"
            else
                # warn — continue but note it
                val_result="$val_result | Verification: FAILED (warned)"
                log_decision "$mission" "$task_id" "Verification failed (warned): $verify_feedback"
            fi
        elif [[ $verify_status -eq 2 ]]; then
            printf "  ${YELLOW}⚠ Verification: needs revision${RESET}\n"
            val_result="$val_result | Verification: needs_revision"
        elif [[ $verify_status -eq 0 ]]; then
            printf "  ${GREEN}✓ Verification passed${RESET}\n"
            val_result="$val_result | Verification: passed"
        fi
    fi

    # Success
    local elapsed
    elapsed="$(elapsed_since "$task_start")"
    printf "  ${GREEN}✓ Completed${RESET} ${DIM}(%s)${RESET}\n" "$elapsed"
    set_state "$mission" "$task_id" "completed"

    # Handle synthesis and gap-analysis output files
    case "$task_type" in
        synthesis)
            safe_write "$KNOWLEDGE_DIR/missions/$mission/synthesis.md" "$output"
            ;;
        gap-analysis)
            safe_write "$KNOWLEDGE_DIR/missions/$mission/gap-analysis.md" "$output"
            # Try to extract follow-up JSON
            local followup_json
            followup_json="$(echo "$output" | sed -n '/^```json/,/^```/p' | sed '1d;$d')" || true
            if [[ -n "$followup_json" ]] && echo "$followup_json" | jq . > /dev/null 2>&1; then
                safe_write "$KNOWLEDGE_DIR/execplans/${mission}-followup.json" "$followup_json"
                printf "  ${CYAN}📋 Follow-up mission saved to execplans/${mission}-followup.json${RESET}\n"
            fi
            ;;
    esac

    write_task_note "$mission" "$task_id" "$task_name" "$milestone" "$task_type" "completed" "$expected" "$prompt_text" "$output" "$val_result" "$task_model_name" "$router_decision" "$router_reasoning"
    [[ -n "$router_decision" ]] && append_routing_log "$task_id" "$mission" "${prompt_text:0:100}" "$task_model_name" "$router_reasoning" "$task_type" "completed"
}

# ─── Run a mission ──────────────────────────────────────────────────────────
run_mission() {
    local mission_file="$1"

    if [[ ! -f "$mission_file" ]]; then
        printf "${RED}✗ Mission file not found: %s${RESET}\n" "$mission_file"
        exit 1
    fi
    if ! jq . "$mission_file" > /dev/null 2>&1; then
        printf "${RED}✗ Invalid JSON: %s${RESET}\n" "$mission_file"
        exit 1
    fi

    local mission_name
    mission_name="$(jq -r '.name // "unnamed"' "$mission_file")"
    local mission_slug
    mission_slug="$(slugify "$mission_name")"
    local task_count
    task_count="$(jq '.tasks | length' "$mission_file")"

    # Print header
    printf "\n${BOLD}═══════════════════════════════════════════════════${RESET}\n"
    printf "${BOLD}  Mission: %s${RESET}\n" "$mission_name"
    printf "${BOLD}  Tasks: %d | Model: %s${RESET}\n" "$task_count" "$ACTIVE_MODEL_NAME"
    printf "${BOLD}═══════════════════════════════════════════════════${RESET}\n\n"

    local mission_start
    mission_start=$(date +%s)

    # Create feedback file if it doesn't exist
    local feedback_path="$KNOWLEDGE_DIR/missions/$mission_slug/_feedback.md"
    mkdir -p "$KNOWLEDGE_DIR/missions/$mission_slug"
    if [[ ! -f "$feedback_path" ]]; then
        safe_write "$feedback_path" "# Mission Feedback: $mission_name

<!-- Write global steering notes here. This content is prepended to EVERY task prompt on re-run. -->
"
    fi

    # Execute tasks in order by index
    local i=0
    while [[ $i -lt $task_count ]]; do
        local task_json
        task_json="$(jq -c ".tasks[$i]" "$mission_file")"
        i=$((i + 1))
        execute_task "$mission_slug" "$mission_file" "$task_json" "$i" "$task_count"
    done

    # Write mission index
    write_mission_index "$mission_slug" "$mission_file"

    # Summary
    local completed failed skipped elapsed
    completed="$(jq -r --arg m "$mission_slug" '.[$m] // {} | to_entries | map(select(.value == "completed")) | length' "$STATE_FILE")"
    failed="$(jq -r --arg m "$mission_slug" '.[$m] // {} | to_entries | map(select(.value == "failed")) | length' "$STATE_FILE")"
    skipped="$(jq -r --arg m "$mission_slug" '.[$m] // {} | to_entries | map(select(.value == "skipped")) | length' "$STATE_FILE")"
    elapsed="$(elapsed_since "$mission_start")"

    printf "\n${BOLD}═══════════════════════════════════════════════════${RESET}\n"
    printf "  ${GREEN}Completed: %d${RESET} | ${RED}Failed: %d${RESET} | ${DIM}Skipped: %d${RESET}\n" "$completed" "$failed" "$skipped"
    printf "  ${DIM}Elapsed: %s${RESET}\n" "$elapsed"
    printf "${BOLD}═══════════════════════════════════════════════════${RESET}\n"

    # Decision log summary
    log_decision "$mission_slug" "-" "Run complete: $completed completed, $failed failed, $skipped skipped ($elapsed)"

    # Auto-learn: distill concepts in the background if any tasks completed
    if [[ "$completed" -gt 0 ]]; then
        printf "\n${DIM}⟳ Auto-learning from mission (background)...${RESET}\n"
        cmd_learn "$mission_slug" &>/dev/null &
        disown
    fi
}

# ─── Resolve mission file ───────────────────────────────────────────────────
resolve_mission_file() {
    local arg="$1"
    local candidates=(
        "$arg"
        "$KNOWLEDGE_DIR/execplans/$arg"
        "$KNOWLEDGE_DIR/execplans/$arg.json"
        "$EXAMPLES_DIR/$arg"
        "$EXAMPLES_DIR/$arg.json"
    )
    for c in "${candidates[@]}"; do
        if [[ -f "$c" ]]; then
            echo "$c"
            return 0
        fi
    done
    printf "${RED}✗ Mission file not found: %s${RESET}\n" "$arg" >&2
    printf "  Searched: %s\n" "${candidates[*]}" >&2
    exit 1
}

# ─── Plan command ────────────────────────────────────────────────────────────
cmd_plan() {
    local input=""

    if [[ $# -gt 0 ]]; then
        local arg="$1"
        if [[ -f "$arg" ]]; then
            input="$(cat "$arg")"
        else
            input="$*"
        fi
    elif [[ ! -t 0 ]]; then
        input="$(cat -)"
    else
        printf "${RED}✗ No input provided. Usage: ./mission.sh plan '<description>' or echo '...' | ./mission.sh plan${RESET}\n"
        exit 1
    fi

    printf "${CYAN}⟳ Generating mission plan...${RESET}\n"

    local plan_prompt="You are a mission planner for a task execution harness. Your ONLY job is to output valid JSON. Do not explain, do not converse, do not add any text before or after the JSON.

Break the following request into 5-15 concrete, executable tasks.

YOU MUST OUTPUT ONLY THIS JSON STRUCTURE — NO OTHER TEXT:
{
  \"name\": \"mission name\",
  \"description\": \"brief description\",
  \"tasks\": [
    {
      \"id\": \"short-kebab-id\",
      \"name\": \"Human readable name\",
      \"milestone\": \"What phase this belongs to\",
      \"type\": \"code|research|synthesis|gap-analysis\",
      \"prompt\": \"Fully self-contained prompt. Include ALL context needed — do not reference other tasks.\",
      \"expected\": \"What success looks like\",
      \"validation\": \"Shell command that exits 0 on success (e.g., test -f file.py, pytest tests/)\",
      \"preconditions\": [\"task-id-that-must-complete-first\"]
    }
  ]
}

Rules:
- Output ONLY the JSON object. No markdown fences, no explanation, no preamble.
- Each task prompt must be FULLY self-contained (include all file paths, specs, context)
- Chain preconditions properly (later tasks depend on earlier ones where needed)
- Validation commands must actually verify the work was done
- Use appropriate types: 'code' for implementation, 'research' for investigation, 'synthesis' for combining findings, 'gap-analysis' for identifying unknowns
- Keep task IDs short and descriptive (kebab-case)

The request:
$input"

    local plan_file
    plan_file="$(mktemp)"
    claude -p --output-format text "$plan_prompt" > "$plan_file" 2>&1

    # Extract JSON — try fenced block first, then use python to find outermost {} object
    local json_content
    json_content="$(sed -n '/^```json/,/^```/p' "$plan_file" | sed '1d;$d')"
    if [[ -z "$json_content" ]] || ! echo "$json_content" | jq . > /dev/null 2>&1; then
        # Use python to extract the outermost JSON object (handles nested braces correctly)
        json_content="$(python3 -c "
import sys, re
text = open('$plan_file').read()
# Find outermost { ... }
depth = 0
start = None
for i, c in enumerate(text):
    if c == '{':
        if depth == 0:
            start = i
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0 and start is not None:
            print(text[start:i+1])
            break
" 2>/dev/null)"
    fi

    # Validate JSON
    if [[ -z "$json_content" ]] || ! echo "$json_content" | jq . > /dev/null 2>&1; then
        printf "${RED}✗ Generated plan is not valid JSON.${RESET}\n"
        printf "Raw output saved to: %s\n" "$plan_file"
        printf "${DIM}Try rephrasing as a concrete task, e.g: clu plan 'research X' or clu plan 'build Y'${RESET}\n"
        exit 1
    fi

    local plan_name
    plan_name="$(echo "$json_content" | jq -r '.name // "unnamed-plan"')"
    local plan_slug
    plan_slug="$(slugify "$plan_name")"
    local plan_path="$KNOWLEDGE_DIR/execplans/$plan_slug.json"

    # Show summary
    printf "\n${BOLD}Mission: %s${RESET}\n" "$plan_name"
    printf "${DIM}%s${RESET}\n\n" "$(echo "$json_content" | jq -r '.description // ""')"

    echo "$json_content" | jq -r '.tasks[] | "  \(.id): \(.name) [\(.type // "code")]"'
    printf "\n"

    safe_write "$plan_path" "$json_content"
    printf "${GREEN}✓ Plan saved to %s${RESET}\n\n" "$plan_path"

    # Confirmation
    printf "Execute this mission? [y/N] "
    read -r confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        run_mission "$plan_path"
    else
        printf "${DIM}Plan saved but not executed.${RESET}\n"
    fi
}

# ─── Research command ────────────────────────────────────────────────────────
cmd_research() {
    local question="$*"

    if [[ -z "$question" ]]; then
        printf "${RED}✗ No research question provided.${RESET}\n"
        printf "Usage: ./mission.sh research 'your question here'\n"
        exit 1
    fi

    printf "${CYAN}⟳ Generating research mission...${RESET}\n"

    local research_prompt="You are a research mission planner. Given a research question, create a mission with 3-5 research tasks approaching the question from different angles, followed by a synthesis task and a gap-analysis task.

Output ONLY valid JSON with this schema:
{
  \"name\": \"research-<topic-slug>\",
  \"description\": \"Research mission: <question>\",
  \"tasks\": [
    {
      \"id\": \"short-kebab-id\",
      \"name\": \"Human readable name\",
      \"milestone\": \"Research|Synthesis|Gap Analysis\",
      \"type\": \"research|synthesis|gap-analysis\",
      \"prompt\": \"Fully self-contained research prompt\",
      \"expected\": \"What good findings look like\",
      \"preconditions\": []
    }
  ]
}

Research angles to consider (pick 3-5 most relevant):
- Industry reports and market analysis
- Technical specifications and documentation
- Competitor/alternative analysis
- Practitioner interviews, forums, real-world experience
- Academic papers and theoretical foundations

The synthesis task should have all research tasks as preconditions.
The gap-analysis task should have the synthesis task as a precondition.

Research question:
$question"

    local plan_file
    plan_file="$(mktemp)"
    claude -p --output-format text "$research_prompt" > "$plan_file" 2>&1

    local json_content
    json_content="$(sed -n '/^```json/,/^```/p' "$plan_file" | sed '1d;$d')"
    if [[ -z "$json_content" ]] || ! echo "$json_content" | jq . > /dev/null 2>&1; then
        json_content="$(python3 -c "
import sys
text = open('$plan_file').read()
depth = 0
start = None
for i, c in enumerate(text):
    if c == '{':
        if depth == 0:
            start = i
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0 and start is not None:
            print(text[start:i+1])
            break
" 2>/dev/null)"
    fi

    if [[ -z "$json_content" ]] || ! echo "$json_content" | jq . > /dev/null 2>&1; then
        printf "${RED}✗ Generated plan is not valid JSON.${RESET}\n"
        printf "Raw output saved to: %s\n" "$plan_file"
        exit 1
    fi

    local plan_name
    plan_name="$(echo "$json_content" | jq -r '.name // "unnamed-research"')"
    local plan_slug
    plan_slug="$(slugify "$plan_name")"
    local plan_path="$KNOWLEDGE_DIR/execplans/$plan_slug.json"

    # Show summary
    printf "\n${BOLD}Research Mission: %s${RESET}\n\n" "$plan_name"
    echo "$json_content" | jq -r '.tasks[] | "  \(.id): \(.name) [\(.type)]"'
    printf "\n"

    safe_write "$plan_path" "$json_content"
    printf "${GREEN}✓ Plan saved to %s${RESET}\n\n" "$plan_path"

    printf "Execute this research mission? [y/N] "
    read -r confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        run_mission "$plan_path"
    else
        printf "${DIM}Plan saved but not executed.${RESET}\n"
    fi
}

# ─── Memory system ────────────────────────────────────────────────────────────
GRID_MEMORY_FILE="$KNOWLEDGE_DIR/grid-memory.md"

load_memory_context() {
    # Returns memory content to prepend to prompts
    if [[ -f "$GRID_MEMORY_FILE" ]]; then
        printf '%s' "$(cat "$GRID_MEMORY_FILE")"
    fi
}

cmd_remember() {
    local fact="$*"
    if [[ -z "$fact" ]]; then
        printf "${RED}✗ Nothing to remember.${RESET}\n"
        printf "Usage: ./mission.sh remember 'my name is Nayak'\n"
        return 1
    fi
    mkdir -p "$(dirname "$GRID_MEMORY_FILE")"
    # Append fact with timestamp
    printf '\n- %s  *(remembered %s)*' "$fact" "$(date '+%Y-%m-%d')" >> "$GRID_MEMORY_FILE"
    printf "${GREEN}✓ Remembered: %s${RESET}\n" "$fact"
}

cmd_forget() {
    local pattern="$*"
    if [[ -z "$pattern" ]]; then
        if [[ -f "$GRID_MEMORY_FILE" ]]; then
            printf "${BOLD}Current memories:${RESET}\n"
            cat "$GRID_MEMORY_FILE"
        else
            printf "${DIM}No memories yet.${RESET}\n"
        fi
        return 0
    fi
    if [[ -f "$GRID_MEMORY_FILE" ]]; then
        local before after
        before="$(wc -l < "$GRID_MEMORY_FILE")"
        grep -v "$pattern" "$GRID_MEMORY_FILE" > "$GRID_MEMORY_FILE.tmp" || true
        mv "$GRID_MEMORY_FILE.tmp" "$GRID_MEMORY_FILE"
        after="$(wc -l < "$GRID_MEMORY_FILE")"
        printf "${GREEN}✓ Removed %d matching memories.${RESET}\n" "$(( before - after ))"
    fi
}

# ─── Knowledge base (concepts extracted from research) ────────────────────────
CONCEPTS_DIR="$KNOWLEDGE_DIR/concepts"

load_relevant_context() {
    # Keyword-search concept files for content relevant to the query
    local query="$1"
    local max_concepts="${2:-3}"
    [[ ! -d "$CONCEPTS_DIR" ]] && return

    # Extract meaningful words (4+ chars, skip common words)
    local keywords
    keywords="$(printf '%s' "$query" | python3 -c "
import sys, re
text = sys.stdin.read().lower()
stopwords = {'this','that','with','from','have','been','will','they','what','when','where','which','your','their','there','about','would','could','should','these','those','other','more','also','into','over','then','than','some','such','only','each','both','much','very','just','like','well','even','most','many','does','used','need','make','work','here','same','back','take','come','good','know','time','look','only','over','also','use','its','its','how','can','are','but','not','the','and','for','you','him','her','was'}
words = re.findall(r'\b[a-z]{4,}\b', text)
keywords = [w for w in words if w not in stopwords]
# Deduplicate preserving order
seen = set()
unique = []
for w in keywords:
    if w not in seen:
        seen.add(w)
        unique.append(w)
print(' '.join(unique[:8]))
" 2>/dev/null)" || keywords=""

    [[ -z "$keywords" ]] && return

    # Score each concept file by keyword hit count
    local results
    results="$(python3 -c "
import os, re, sys
concepts_dir = '$CONCEPTS_DIR'
keywords = '$keywords'.split()
files = [f for f in os.listdir(concepts_dir) if f.endswith('.md')]
scores = []
for fname in files:
    path = os.path.join(concepts_dir, fname)
    try:
        content = open(path).read().lower()
        score = sum(content.count(k) for k in keywords)
        if score > 0:
            scores.append((score, fname, path))
    except:
        pass
scores.sort(reverse=True)
for score, fname, path in scores[:$max_concepts]:
    print(path)
" 2>/dev/null)" || results=""

    [[ -z "$results" ]] && return

    local context=""
    while IFS= read -r fpath; do
        [[ -z "$fpath" ]] && continue
        # Extract title and key sections (skip frontmatter, take first 600 chars of content)
        local snippet
        snippet="$(python3 -c "
import sys, re
content = open('$fpath' if '$fpath' else sys.argv[1]).read()
# Strip frontmatter
content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
# Get title from filename or first heading
fname = os.path.basename('$fpath').replace('.md', '').replace('-', ' ')
import os
fname = os.path.basename('$fpath').replace('.md', '').replace('-', ' ')
# Trim to first 600 chars
content = content.strip()[:600]
print(f'[{fname}]\n{content}')
" 2>/dev/null)"
        [[ -n "$snippet" ]] && context="${context}${snippet}\n\n"
    done <<< "$results"

    if [[ -n "$context" ]]; then
        printf '--- Relevant prior research ---\n'
        printf '%s' "$context"
        printf '--- End prior research ---\n\n'
    fi
}

cmd_learn() {
    # Extract key concepts from a completed mission and save to knowledge/concepts/
    local mission_slug="$1"
    if [[ -z "$mission_slug" ]]; then
        # List available missions to learn from
        printf "${BOLD}Available missions to learn from:${RESET}\n"
        if [[ -d "$KNOWLEDGE_DIR/missions" ]]; then
            for d in "$KNOWLEDGE_DIR/missions"/*/; do
                [[ -d "$d" ]] && printf "  %s\n" "$(basename "$d")"
            done
        fi
        printf "\nUsage: ./mission.sh learn <mission-slug>\n"
        return 0
    fi

    local mission_dir="$KNOWLEDGE_DIR/missions/$mission_slug"
    if [[ ! -d "$mission_dir" ]]; then
        printf "${RED}✗ Mission not found: %s${RESET}\n" "$mission_slug"
        exit 1
    fi

    mkdir -p "$CONCEPTS_DIR"
    local concept_path="$CONCEPTS_DIR/${mission_slug}.md"

    printf "${CYAN}⟳ Extracting concepts from: %s${RESET}\n" "$mission_slug"

    # Gather all task output (skip index/feedback files)
    local all_content=""
    for note in "$mission_dir"/*.md; do
        local basename
        basename="$(basename "$note")"
        [[ "$basename" == _* ]] && continue
        all_content="${all_content}

=== $basename ===
$(cat "$note")
"
    done

    if [[ -z "$all_content" ]]; then
        printf "${RED}✗ No task notes found in %s${RESET}\n" "$mission_dir"
        exit 1
    fi

    local extraction_prompt="You are a knowledge distiller. Extract and structure the key concepts, findings, and reusable knowledge from this research mission.

Mission: $mission_slug

Research content:
${all_content:0:8000}

Output a markdown document with these sections:
1. ## Summary (2-3 sentences: what this research covers)
2. ## Key Findings (bullet points of the most important discoveries)
3. ## Key Concepts (definitions/explanations of domain terms discovered)
4. ## Actionable Insights (what can be built on or referenced later)
5. ## Open Questions (unresolved questions for future research)

Be concise and factual. Focus on content that will be useful context for future questions."

    # Use local model for extraction (summarization — local handles this well)
    local model_cmd model_name
    model_cmd="$(get_model_cmd "local" 2>/dev/null)" || model_cmd=""
    model_name="local"
    if [[ -z "$model_cmd" ]]; then
        model_cmd="$(get_model_cmd "claude" 2>/dev/null)" || true
        model_name="claude"
    fi

    local log_file
    log_file="$(mktemp)"
    run_prompt "$extraction_prompt" "$log_file" "$model_cmd" "$model_name" || true

    local output
    output="$(cat "$log_file")"
    if [[ -z "$output" ]]; then
        printf "${RED}✗ Extraction failed.${RESET}\n"
        exit 1
    fi

    # Save concept file
    safe_write "$concept_path" "---
title: $mission_slug
source_mission: $mission_slug
date: $(date '+%Y-%m-%d')
---

$output
"
    printf "${GREEN}✓ Concepts saved to knowledge/concepts/%s.md${RESET}\n" "$mission_slug"
    printf "\n%s\n" "$output"
}

cmd_knowledge() {
    # List or search the knowledge base
    local query="$*"
    if [[ ! -d "$CONCEPTS_DIR" ]] || [[ -z "$(ls "$CONCEPTS_DIR" 2>/dev/null)" ]]; then
        printf "${DIM}No concepts in knowledge base yet.${RESET}\n"
        printf "Run: ./mission.sh learn <mission-slug>\n"
        return 0
    fi

    if [[ -z "$query" ]]; then
        printf "${BOLD}Knowledge Base:${RESET}\n\n"
        for f in "$CONCEPTS_DIR"/*.md; do
            local title
            title="$(basename "$f" .md)"
            local summary
            summary="$(grep -A2 '## Summary' "$f" 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//')" || summary=""
            printf "  ${CYAN}%-40s${RESET} %s\n" "$title" "${summary:0:60}"
        done
    else
        printf "${BOLD}Searching knowledge base for: %s${RESET}\n\n" "$query"
        local ctx
        ctx="$(load_relevant_context "$query" 5)"
        if [[ -n "$ctx" ]]; then
            printf '%s\n' "$ctx"
        else
            printf "${DIM}No relevant concepts found.${RESET}\n"
        fi
    fi
}

# ─── Conversation history ─────────────────────────────────────────────────────
CONVERSATION_FILE="$MISSION_DIR/conversation.jsonl"

get_conversation_context() {
    # Return last N turns as context for conversational ask mode
    local max_turns="${1:-5}"
    if [[ ! -f "$CONVERSATION_FILE" ]]; then
        return
    fi
    local history=""
    history="$(tail -n "$max_turns" "$CONVERSATION_FILE" | python3 -c "
import sys, json
lines = sys.stdin.read().strip().split('\n')
parts = []
for line in lines:
    if not line.strip():
        continue
    try:
        d = json.loads(line)
        parts.append(f\"User: {d['q']}\nAssistant: {d['a']}\")
    except:
        pass
if parts:
    print('--- Previous conversation ---')
    print('\n\n'.join(parts))
    print('--- End of conversation ---\n')
" 2>/dev/null)" || history=""
    printf '%s' "$history"
}

append_conversation() {
    local question="$1" answer="$2"
    mkdir -p "$(dirname "$CONVERSATION_FILE")"
    python3 -c "
import json, sys
q = sys.argv[1]
a = sys.argv[2][:500]  # truncate long answers
print(json.dumps({'q': q, 'a': a}))
" "$question" "$answer" >> "$CONVERSATION_FILE"
}

clear_conversation() {
    rm -f "$CONVERSATION_FILE"
    printf "${GREEN}✓ Conversation history cleared.${RESET}\n"
}

# ─── Ask command (conversational) ────────────────────────────────────────────
cmd_ask() {
    local question="$*"
    if [[ -z "$question" ]]; then
        printf "${RED}✗ No question provided.${RESET}\n"
        printf "Usage: ./mission.sh ask 'your question'\n"
        exit 1
    fi

    # Special commands
    if [[ "$question" == "/clear" || "$question" == "/new" ]]; then
        clear_conversation
        return 0
    fi

    # Route through router when in auto mode
    local resolved_model="$ACTIVE_MODEL_NAME"
    local resolved_cmd="$ACTIVE_MODEL"
    local routing_reason=""
    if [[ "$ACTIVE_MODEL_NAME" == "auto" || "$ACTIVE_MODEL" == "__auto__" ]]; then
        local route_result
        route_result="$(route_task "ask" "$question" "")"
        resolved_model="${route_result%%|*}"
        routing_reason="${route_result#*|}"
        resolved_cmd="$(get_model_cmd "$resolved_model" 2>/dev/null)" || resolved_cmd=""
        if [[ -z "$resolved_cmd" ]]; then
            resolved_model="claude"
            resolved_cmd="$(get_model_cmd "claude")"
            routing_reason="[no cmd for $resolved_model, fell back] $routing_reason"
        fi
        printf "${CYAN}⟳ Asking auto...${RESET}\n"
        printf "  ${CYAN}⟶ Routed to: %s${RESET} ${DIM}(%s)${RESET}\n" "$resolved_model" "$routing_reason"
    else
        printf "${CYAN}⟳ Asking ${ACTIVE_MODEL_NAME}...${RESET}\n"
    fi

    # Build full prompt with memory + knowledge context + conversation history
    local full_prompt=""

    # Prepend persistent memory (facts about user/context)
    local memory
    memory="$(load_memory_context)"
    if [[ -n "$memory" ]]; then
        full_prompt="Persistent context about the user:
${memory}

"
    fi

    # Inject relevant prior research from knowledge base
    local knowledge_ctx
    knowledge_ctx="$(load_relevant_context "$question" 3)"
    if [[ -n "$knowledge_ctx" ]]; then
        full_prompt="${full_prompt}${knowledge_ctx}"
        printf "  ${DIM}⟶ Injecting relevant knowledge context${RESET}\n" >&2
    fi

    # Prepend conversation history
    local conv_ctx
    conv_ctx="$(get_conversation_context 5)"
    if [[ -n "$conv_ctx" ]]; then
        full_prompt="${full_prompt}${conv_ctx}
"
    fi

    full_prompt="${full_prompt}${question}"

    local log_file
    log_file="$(mktemp)"
    run_prompt "$full_prompt" "$log_file" "$resolved_cmd" "$resolved_model" || true

    local output
    output="$(cat "$log_file")"
    if [[ -z "$output" ]]; then
        printf "${RED}✗ No output from model.${RESET}\n"
        exit 1
    fi
    printf '\n%s\n' "$output"

    # Save conversation turn
    append_conversation "$question" "$output"

    # Save to knowledge/asks/ as a dated markdown note (skip in dory mode)
    if [[ "${DORY_MODE:-0}" == "1" ]]; then
        printf "\n${DIM}Dory mode — nothing saved${RESET}\n"
    else
        local asks_dir="$KNOWLEDGE_DIR/asks"
        mkdir -p "$asks_dir"
        local slug
        slug="$(slugify "${question:0:50}")"
        local note_path="$asks_dir/${slug}.md"
        local model_display="$resolved_model"
        [[ "$ACTIVE_MODEL_NAME" == "auto" ]] && model_display="auto → $resolved_model"
        safe_write "$note_path" "---
date: $(date '+%Y-%m-%d %H:%M')
model: $model_display
routed_to: $resolved_model
routing_reason: '$(printf '%s' "$routing_reason" | sed "s/'/''/g")'
---

## Question

$question

## Answer

$output
"
        printf "\n${DIM}Saved to knowledge/asks/%s.md${RESET}\n" "$slug"
    fi
}

# ─── Review command ──────────────────────────────────────────────────────────
cmd_review() {
    local mission_slug="$1"
    local mission_dir="$KNOWLEDGE_DIR/missions/$mission_slug"

    if [[ ! -d "$mission_dir" ]]; then
        printf "${RED}✗ Mission not found: %s${RESET}\n" "$mission_slug"
        exit 1
    fi

    printf "${CYAN}⟳ Reviewing mission: %s${RESET}\n" "$mission_slug"

    local all_content=""
    for note in "$mission_dir"/*.md; do
        [[ "$(basename "$note")" == _* ]] && continue
        [[ "$(basename "$note")" == "synthesis.md" ]] && continue
        [[ "$(basename "$note")" == "gap-analysis.md" ]] && continue
        [[ "$(basename "$note")" == "review.md" ]] && continue
        all_content="$all_content
=== $(basename "$note" .md) ===
$(cat "$note")
"
    done

    # Include synthesis if it exists
    if [[ -f "$mission_dir/synthesis.md" ]]; then
        all_content="$all_content
=== Synthesis ===
$(cat "$mission_dir/synthesis.md")
"
    fi

    local review_prompt="Review all findings and researcher notes from this mission.

$all_content

Answer these questions:
1. What should we investigate next?
2. What assumptions are still untested?
3. What did the researcher flag (in 'My Notes' sections) that changes our approach?
4. What are the strongest and weakest pieces of evidence?
5. What decisions can we now make with confidence?

Also generate a follow-up mission as valid JSON (with tasks array) to address the gaps."

    local log_file="$LOGS_DIR/review-$mission_slug.log"
    run_prompt "$review_prompt" "$log_file"

    local output=""
    [[ -f "$log_file" ]] && output="$(cat "$log_file")"

    safe_write "$mission_dir/review.md" "$output"
    printf "${GREEN}✓ Review saved to %s/review.md${RESET}\n" "$mission_dir"

    # Try to extract follow-up JSON
    local followup_json
    followup_json="$(echo "$output" | sed -n '/^```json/,/^```/p' | sed '1d;$d')" || true
    if [[ -n "$followup_json" ]] && echo "$followup_json" | jq . > /dev/null 2>&1; then
        safe_write "$KNOWLEDGE_DIR/execplans/${mission_slug}-review-followup.json" "$followup_json"
        printf "${CYAN}📋 Follow-up mission saved to execplans/${mission_slug}-review-followup.json${RESET}\n"
    fi
}

# ─── Status command ──────────────────────────────────────────────────────────
cmd_status() {
    local mission_slug="${1:-}"

    if [[ -z "$mission_slug" ]]; then
        # List all missions
        printf "${BOLD}All Missions:${RESET}\n\n"
        local missions
        missions="$(jq -r 'keys[]' "$STATE_FILE")"
        if [[ -z "$missions" ]]; then
            printf "  ${DIM}No missions found.${RESET}\n"
            return 0
        fi
        while IFS= read -r m; do
            local total completed failed skipped
            total="$(jq -r --arg m "$m" '.[$m] | length' "$STATE_FILE")"
            completed="$(jq -r --arg m "$m" '.[$m] | to_entries | map(select(.value == "completed")) | length' "$STATE_FILE")"
            failed="$(jq -r --arg m "$m" '.[$m] | to_entries | map(select(.value == "failed")) | length' "$STATE_FILE")"
            skipped="$(jq -r --arg m "$m" '.[$m] | to_entries | map(select(.value == "skipped")) | length' "$STATE_FILE")"
            local pct=0
            [[ $total -gt 0 ]] && pct=$((completed * 100 / total))
            printf "  ${BOLD}%s${RESET} — %d%% (%d/%d completed" "$m" "$pct" "$completed" "$total"
            [[ $failed -gt 0 ]] && printf ", ${RED}%d failed${RESET}" "$failed"
            [[ $skipped -gt 0 ]] && printf ", ${DIM}%d skipped${RESET}" "$skipped"
            printf ")\n"
        done <<< "$missions"
    else
        # Show specific mission
        printf "${BOLD}Mission: %s${RESET}\n\n" "$mission_slug"
        local tasks
        tasks="$(jq -r --arg m "$mission_slug" '.[$m] // {} | to_entries[] | "\(.key): \(.value)"' "$STATE_FILE")"
        if [[ -z "$tasks" ]]; then
            printf "  ${DIM}No state found for this mission.${RESET}\n"
            return 0
        fi
        while IFS= read -r line; do
            local tid="${line%%:*}"
            local tstate="${line#*: }"
            case "$tstate" in
                completed) printf "  ${GREEN}✓${RESET} %s\n" "$tid" ;;
                failed)    printf "  ${RED}✗${RESET} %s\n" "$tid" ;;
                skipped)   printf "  ${DIM}⊘${RESET} %s\n" "$tid" ;;
                running)   printf "  ${YELLOW}▸${RESET} %s\n" "$tid" ;;
                *)         printf "  ${DIM}○${RESET} %s\n" "$tid" ;;
            esac
        done <<< "$tasks"
    fi
}

# ─── Models command ──────────────────────────────────────────────────────────
cmd_models() {
    printf "${BOLD}Available Models:${RESET}\n\n"
    # Show the virtual 'auto' model first
    if [[ "$ACTIVE_MODEL_NAME" == "auto" ]]; then
        printf "  ${GREEN}▸ auto${RESET} = route each task via router ${GREEN}(active)${RESET}\n"
    else
        printf "  ${DIM}  auto${RESET} = route each task via router\n"
    fi
    local name cmd
    while IFS= read -r name; do
        [[ -z "$name" ]] && continue
        cmd="$(get_model_cmd "$name")"
        if [[ "$name" == "$ACTIVE_MODEL_NAME" ]]; then
            printf "  ${GREEN}▸ %s${RESET} = %s ${GREEN}(active)${RESET}\n" "$name" "$cmd"
        else
            printf "  ${DIM}  %s${RESET} = %s\n" "$name" "$cmd"
        fi
    done <<< "$(list_model_names)"
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
    ensure_dirs
    load_models

    local flag_model=""
    # Parse --model and --route-override flags
    local args=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --model)
                flag_model="$2"
                shift 2
                ;;
            --model=*)
                flag_model="${1#*=}"
                shift
                ;;
            --route-override)
                ROUTE_OVERRIDE="$2"
                shift 2
                ;;
            --route-override=*)
                ROUTE_OVERRIDE="${1#*=}"
                shift
                ;;
            --dory)
                DORY_MODE="1"
                shift
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done
    set -- "${args[@]+"${args[@]}"}"

    resolve_model "$flag_model"

    if [[ $# -eq 0 ]]; then
        printf "${BOLD}Grid Mission Control${RESET}\n\n"
        printf "Usage:\n"
        printf "  ./mission.sh ask '<question>'         Ask a question (conversational)\n"
        printf "  ./mission.sh plan '<description>'     Generate & run a multi-task mission\n"
        printf "  ./mission.sh research '<question>'    Generate & run a research mission\n"
        printf "  ./mission.sh <file>                  Run a mission from JSON file\n"
        printf "  ./mission.sh review <mission-name>    Review a completed mission\n"
        printf "  ./mission.sh status [mission-name]    Show mission status\n"
        printf "  ./mission.sh models                   List available models\n"
        printf "  ./mission.sh remember '<fact>'        Teach Grid something to remember\n"
        printf "  ./mission.sh forget [pattern]         View or remove memories\n"
        printf "  ./mission.sh clear                    Clear conversation history\n"
        printf "  ./mission.sh learn [mission-slug]     Extract concepts from a mission\n"
        printf "  ./mission.sh knowledge [query]        Browse or search knowledge base\n"
        printf "\nOptions:\n"
        printf "  --model <name>             Override model (or set MODEL env var)\n"
        printf "  --route-override <backend> Force backend: claude|local (skips router)\n"
        printf "  --dory                     Ephemeral mode (nothing saved to disk)\n"
        printf "\nRouting:\n"
        printf "  Default model is 'auto' — each task is routed by a local LLM (qwen3:4b).\n"
        printf "  Configure the router in .mission/models.conf: router=ollama run qwen3:4b\n"
        printf "  Routing decisions are logged to .mission/routing-log.jsonl\n"
        exit 0
    fi

    local cmd="$1"
    shift

    case "$cmd" in
        ask)        cmd_ask "$@" ;;
        plan)       cmd_plan "$@" ;;
        research)   cmd_research "$@" ;;
        review)     cmd_review "$@" ;;
        status)     cmd_status "$@" ;;
        models)     cmd_models ;;
        remember)   cmd_remember "$@" ;;
        forget)     cmd_forget "$@" ;;
        clear)      clear_conversation ;;
        learn)      cmd_learn "$@" ;;
        knowledge)  cmd_knowledge "$@" ;;
        *)
            local mission_file
            mission_file="$(resolve_mission_file "$cmd")"
            run_mission "$mission_file"
            ;;
    esac
}

main "$@"
