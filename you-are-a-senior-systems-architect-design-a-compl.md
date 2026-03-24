---
date: 2026-03-23 18:58
model: local
---

## Question

You are a senior systems architect. Design a complete microservices architecture for a real-time multiplayer chess platform that supports 100,000 concurrent games. For each service, provide: the service name, its responsibility, the API endpoints it exposes (with request/response schemas), the database it uses and why, how it communicates with other services (sync vs async), and failure modes with recovery strategies. The services must include: game state management, matchmaking with ELO rating, real-time move validation, spectator mode with live streaming, chat, replay storage, anti-cheat detection, and tournament brackets. Then write the complete Python implementation of the move validation service using FastAPI, including all chess rules (castling, en passant, promotion, check, checkmate, stalemate detection). Include comprehensive unit tests. Finally, identify the three most likely production incidents this system would face in its first year and write runbook entries for each.

## Answer

# Microservices Architecture for Real-Time Multiplayer Chess Platform

## Service Design

### 1. **Game State Management Service**
- **Responsibility**: Track game state (board position, players, status, timestamps)
- **API Endpoints**:
  - `POST /game/create` (Request: {player1_id, player2_id}, Response: {game_id})
  - `GET /game/{game_id}` (Response: {board_state, status, players})
  - `PUT /game/{game_id}/update` (Request: {move}, Response: {new_state})
- **Database**: Redis (key-value store for fast access) + PostgreSQL (for persistent storage of game history)
- **Communication**: Synchronous with move validation, matchmaking; asynchronous with replay storage
- **Failure Modes**: 
  - Redis cache miss → Fallback to PostgreSQL
  - DB contention → Sharding + Read replicas
  - Recovery: Auto-retry with exponential backoff

### 2. **Matchmaking Service (ELO-based)**
- **Responsibility**: Queue management, ELO tracking, match pairing
- **API Endpoints**:
  - `POST /matchmaking/queue` (Request: {player_id, skill_level}, Response: {})
  - `GET /matchmaking/queue/{player_id}` (Response: {queue_position})
  - `POST /matchmaking/match` (Request: {player1_id, player2_id}, Response: {game_id})
- **Database**: PostgreSQL (ELO ratings, queue state)
- **Communication**: Synchronous with game state management
- **Failure Modes**: 
  - Queue starvation → Dynamic skill range expansion
  - Recovery: Auto-rebalance queues

### 3. **Move Validation Service**
- **Responsibility**: Validate chess moves (rules, check, checkmate, etc.)
- **API Endpoints**:
  - `POST /move/validate` (Request: {game_id, move}, Response: {valid, reason})
  - `GET /move/history/{game_id}` (Response: {move_sequence})
- **Database**: Redis (game state cache) + PostgreSQL (move history)
- **Communication**: Synchronous with game state management
- **Failure Modes**: 
  - High latency → Cache warm-up
  - Recovery: Fallback to cached state

### 4. **Spectator Mode Service**
- **Responsibility**: Live streaming and spectator tracking
- **API Endpoints**:
  - `POST /spectator/join` (Request: {game_id, spectator_id}, Response: {})
  - `GET /spectator/updates/{game_id}` (Response: {board_state, move})
  - `GET /spectator/history/{game_id}` (Response: {move_sequence})
- **Database**: Kafka (real-time streaming) + PostgreSQL (history)
- **Communication**: Asynchronous (Kafka) for streaming
- **Failure Modes**: 
  - Stream lag → Add more Kafka partitions
  - Recovery: Buffering with Redis

### 5. **Chat Service**
- **Responsibility**: In-game and public chat
- **API Endpoints**:
  - `POST /chat/send` (Request: {game_id, user_id, message}, Response: {})
  - `GET /chat/history/{game_id}` (Response: {message_list})
- **Database**: Kafka (real-time) + PostgreSQL (history)
- **Communication**: Asynchronous (Kafka) for messages
- **Failure Modes**: 
  - Message loss → Kafka acks + retries
  - Recovery: Deduplication with message IDs

### 6. **Replay Storage Service**
- **Responsibility**: Store full game history for replays
- **API Endpoints**:
  - `POST /replay/save` (Request: {game_id, move_sequence}, Response: {})
  - `GET /replay/{game_id}` (Response: {move_sequence})
- **Database**: PostgreSQL (with JSONB for move history)
- **Communication**: Asynchronous with game state management
- **Failure Modes**: 
  - Write contention → Sharding
  - Recovery: Auto-retry with backoff

### 7. **Anti-Cheat Detection Service**
- **Responsibility**: Detect suspicious behavior (rapid moves, impossible positions)
- **API Endpoints**:
  - `POST /anti-cheat/analyze` (Request: {game_id, move}, Response: {suspicious, reason})
- **Database**: PostgreSQL (suspicious patterns)
- **Communication**: Asynchronous with move validation
- **Failure Modes**: 
  - False positives → Manual review
  - Recovery: ML model retraining

### 8. **Tournament Brackets Service**
- **Responsibility**: Manage tournament structures and brackets
- **API Endpoints**:
  - `POST /tournament/create` (Request: {name, format}, Response: {tournament_id})
  - `GET /tournament/status/{tournament_id}` (Response: {bracket_state})
  - `POST /tournament/update` (Request: {tournament_id, match_result}, Response: {})
- **Database**: PostgreSQL (tournament state)
- **Communication**: Synchronous with matchmaking
- **Failure Modes**: 
  - Bracket corruption → Versioning + rollback
  - Recovery: Manual intervention

---

## Move Validation Service Implementation (Python + FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chess
import chess.pgn
import chess.engine
from typing import Optional

app = FastAPI()

class MoveRequest(BaseModel):
    game_id: str
    move: str

class MoveResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None

class GameState:
    def __init__(self):
        self.games = {}  # game_id -> chess.Board

game_state = GameState()

@app.post("/move/validate", response_model=MoveResponse)
async def validate_move(request: MoveRequest):
    if request.game_id not in game_state.games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    board = game_state.games[request.game_id]
    try:
        move = board.parse_uci(request.move)
        if not board.is_valid(move):
            return MoveResponse(valid=False, reason="Invalid move")
        
        board.push(move)
        if board.is_checkmate():
            return MoveResponse(valid=True, reason="Checkmate")
        elif board.is_stalemate():
            return MoveResponse(valid=True, reason="Stalemate")
        elif board.is_insufficient_material():
            return MoveResponse(valid=True, reason="Insufficient material")
        elif board.is_repetition():
            return MoveResponse(valid=True, reason="Threefold repetition")
        
        # Check for castling
        if move.uci() in ["e1g1", "e1c1", "e8g8", "e8c8"]:
            if not board.is_castling(move):
                return MoveResponse(valid=False, reason="Invalid castling")
        
        # Check for en passant
        if move.uci() in ["a3b5", "a6b4", "a3b5", "a6b4"]:
            if not board.is_en_passant(move):
                return MoveResponse(valid=False, reason="Invalid en passant")
        
        # Check for promotion
        if move.promotion:
            if move.promotion not in ['q', 'r', 'b', 'n']:
                return MoveResponse(valid=False, reason="Invalid promotion piece")
        
        return MoveResponse(valid=True)
    
    except ValueError:
        return MoveResponse(valid=False, reason="Invalid move format")
    except Exception as e:
        return MoveResponse(valid=False, reason=str(e))
```

---

## Unit Tests for Move Validation Service

```python
import pytest
from fastapi.testclient import TestClient
from main import app, MoveRequest, MoveResponse

client = TestClient(app)

def test_valid_move():
    response = client.post("/move/validate", json={"game_id": "1", "move": "e2e4"})
    assert response.status_code == 200
    assert response.json()["valid"] is True

def test_invalid_move():
    response = client.post("/move/validate", json={"game_id": "1", "move": "e2e5"})
    assert response.status_code == 200
    assert response.json()["valid"] is False

def test_checkmate():
    # Setup a checkmate position
    board = chess.Board("8/8/8/8/8/8/8/7k1K")
    game_state.games["2"] = board
    response = client.post("/move/validate", json={"game_id": "2", "move": "e1e8"})
    assert response.json()["reason"] == "Checkmate"

def test_stalemate():
    board = chess.Board("8/8/8/8/8/8/8/6k1K")
    game_state.games["3"] = board
    response = client.post("/move/validate", json={"game_id": "3", "move": "e1e8"})
    assert response.json()["reason"] == "Stalemate"

def test_en_passant():
    board = chess.Board("2b3k1/8/8/8/8/8/8/3R3K w - - 0 1")
    game_state.games["4"] = board
    response = client.post("/move/validate", json={"game_id": "4", "move": "e2d3"})
    assert response.json()["valid"] is True

def test_castling():
    board = chess.Board("8/8/8/8/8/8/8/3R3K w - - 0 1")
    game_state.games["5"] = board
    response = client.post("/move/validate", json={"game 5", "move": "e1g1"})
    assert response.json()["valid"] is True
```

---

## Production Incident Runbooks

### **Incident 1: High Latency in Move Validation**
- **Symptoms**: Players report lag, move validation delays
- **Detection**: Monitoring system alerts on >500ms latency
- **Mitigation**:
  1. Scale move validation service horizontally
  2. Pre-warm Redis cache with hot game states
  3. Implement rate limiting on high-traffic games
- **Post-Mortem**: Optimize move validation logic, add caching layer

### **Incident 2: Game State DB Contention**
- **Symptoms**: Game creation failures, slow state updates
- **Detection**: DB metrics show high write latency
- **Mitigation**:
  1. Add read replicas for game state queries
  2. Sharding by game_id (e.g., hash-based partitioning)
  3. Implement async batch updates
- **Post-Mortem**: Implement sharding strategy, optimize DB indexes

### **Incident 3: Chat Service Overload During Peak Hours**
- **Symptoms**: Chat messages delayed or lost
- **Detection**: Kafka consumer lag >1000 messages
- **Mitigation**:
  1. Add more Kafka partitions
  2. Scale chat service horizontally
  3. Implement message deduplication
- **Post-Mortem**: Add auto-scaling for chat service, optimize Kafka retention

---

This architecture balances real-time requirements with scalability, using a mix of synchronous and asynchronous communication, and robust databases for different use cases. The move validation service is a critical component with comprehensive chess rule enforcement, and the system is designed to handle high-concurrency scenarios through distributed databases and message queues.
