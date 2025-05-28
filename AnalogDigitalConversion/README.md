# Analog-Digital Conversion Module

This module demonstrates audio signal processing with different sampling rates and bit depths, along with quality analysis using Signal-to-Noise Ratio (SNR) measurements.

## Features

- Audio recording from microphone
- Audio playback
- Sample rate conversion (8000Hz, 16000Hz, 44100Hz, 48000Hz)
- Bit depth conversion (8-bit, 16-bit)
- SNR calculation for quality assessment
- WAV file handling

## Requirements

- Python 3.x
- pyaudio
- numpy
- scipy
- soundfile

## Installation

Install the required dependencies:
```bash
pip install pyaudio numpy scipy soundfile
```

## Usage

Run the main script:
```bash
python main.py
```

The program offers two main options:
1. Record audio and process it with different parameters
2. Play existing WAV files

### Recording and Processing

When you choose option 1, the program will:
1. Record a reference audio sample
2. Process it with different sample rates and bit depths
3. Calculate and display SNR values for each processed version
4. Save all versions as WAV files

### Playing Audio

When you choose option 2, the program will play all WAV files in the current directory.

## Output Files

The program generates the following files:
- `reference.wav`: Original recording
- `audio_[sample_rate]Hz_[bit_depth]bit.wav`: Processed versions with different parameters

## SNR Analysis

Signal-to-Noise Ratio (SNR) is calculated for each processed version to assess the quality of the conversion. Higher SNR values indicate better quality. 