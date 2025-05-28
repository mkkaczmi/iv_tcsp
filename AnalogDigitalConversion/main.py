import pyaudio
import wave
import numpy as np
import soundfile as sf
from scipy import signal

def record_audio(duration=5, sample_rate=48000, bit_depth=16):
    """Record audio from microphone"""
    p = pyaudio.PyAudio()
    format = pyaudio.paInt16 if bit_depth == 16 else pyaudio.paInt8
    
    stream = p.open(
        format=format,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=1024
    )

    print("Recording...")
    frames = []
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return frames, sample_rate, bit_depth

def save_audio(frames, filename, sample_rate, bit_depth):
    """Save audio to WAV file"""
    p = pyaudio.PyAudio()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16 if bit_depth == 16 else pyaudio.paInt8))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    p.terminate()

def play_audio(filename):
    """Play audio from WAV file"""
    p = pyaudio.PyAudio()
    wf = wave.open(filename, 'rb')
    
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()

def process_audio(input_file, sample_rate, bit_depth):
    """Process audio with different sample rate and bit depth"""
    data, sr = sf.read(input_file)
    
    # Resample if needed
    if sr != sample_rate:
        data = signal.resample(data, int(len(data) * sample_rate / sr))
    
    # Apply bit depth conversion
    if bit_depth == 8:
        data = np.int8(data * 127)
        data = data.astype(np.float32) / 127.0
    elif bit_depth == 16:
        data = np.int16(data * 32767)
        data = data.astype(np.float32) / 32767.0

    return data

def calculate_snr(original, processed):
    """Calculate Signal-to-Noise Ratio"""
    min_length = min(len(original), len(processed))
    original = original[:min_length]
    processed = processed[:min_length]
    
    signal_power = np.mean(original ** 2)
    noise_power = np.mean((original - processed) ** 2)
    return 10 * np.log10(signal_power / noise_power)

def main():
    print("1. Record audio")
    print("2. Play audio")
    choice = int(input("Choose option: "))

    if choice == 1:
        # Record reference audio
        frames, sr, bits = record_audio()
        reference_file = "reference.wav"
        save_audio(frames, reference_file, sr, bits)
        print(f"Reference recording saved as {reference_file}")

        # Process with different parameters
        sample_rates = [8000, 16000, 44100, 48000]
        bit_depths = [8, 16]
        
        for sr in sample_rates:
            for bits in bit_depths:
                output_file = f"audio_{sr}Hz_{bits}bit.wav"
                processed_data = process_audio(reference_file, sr, bits)
                sf.write(output_file, processed_data, sr)
                
                original_data, _ = sf.read(reference_file)
                snr = calculate_snr(original_data, processed_data)
                print(f"SNR for {output_file}: {snr:.2f} dB")

    elif choice == 2:
        # Play all WAV files
        import os
        for file in os.listdir():
            if file.endswith(".wav"):
                print(f"Playing {file}...")
                play_audio(file)

if __name__ == "__main__":
    main()
