import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from scipy.io.wavfile import read

# Convert MP3 to WAV using PyDub
def load_audio(file_path):
    audio = AudioSegment.from_mp3(file_path)
    wav_data =audio.raw_data
    sample_rate = audio.frame_rate
    return np.frombuffer(wav_data, dtype=np.int16), sample_rate

# FFT analysis
def analyze_frequencies(signal, sample_rate):
    n_samples = len(signal)
    fft_result = np.fft.fft(signal)/n_samples  # Normalize
    frequencies = np.fft.fftfreq(n_samples, 1/sample_rate)
    
    # Take only positive frequencies (first half)
    positive_freqs = frequencies[:n_samples//2]
    magnitude = 2 * abs(fft_result)[:n_samples//2]  # Double amplitude for single-sided spectrum
    return positive_freqs, magnitude

# Plot frequency spectrum
def plot_spectrum(frequencies, magnitudes):
    plt.figure(figsize=(14, 6))
    plt.plot(frequencies, magnitudes, 'b')
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

# Main execution
if __name__ == "__main__":
    file_path = input("Enter MP3 file path: ")
    try:
        signal, sample_rate = load_audio(file_path)
        frequencies, magnitude = analyze_frequencies(signal, sample_rate)
        plot_spectrum(frequencies, magnitude)
    except Exception as e:
        print(f"Error: {e}")