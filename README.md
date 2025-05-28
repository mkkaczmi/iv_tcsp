# TCSP Project

This repository contains implementations of communication protocols, error correction mechanisms, signal processing demonstrations, and data compression techniques.

## Project Structure

The project is organized into four main components:

### 1. XModem Protocol Implementation
Located in the `XModem/` directory, this module implements the XModem protocol for reliable file transfer over serial communication. The implementation includes:
- File transfer capabilities
- Error detection
- Retransmission mechanisms

### 2. Error Correction
Located in the `ErrorCorrection/` directory, this module provides error correction mechanisms for serial communication, including:
- Error detection algorithms
- Error correction techniques
- Data integrity verification

### 3. Analog-Digital Conversion
Located in the `AnalogDigitalConversion/` directory, this module demonstrates audio signal processing with:
- Sample rate conversion
- Bit depth conversion
- Signal quality analysis using SNR
- Audio recording and playback capabilities

### 4. Huffman Encoding
Located in the `HuffmanEncoding/` directory, this module implements data compression using:
- Huffman coding algorithm
- Client-server architecture for data transmission
- Text compression and decompression
- Compression ratio analysis

## Requirements

- Python 3.x
- pyserial==3.5
- pyaudio
- numpy
- scipy
- soundfile
- bitarray

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Each component has its own README file with detailed usage instructions:
- [XModem Protocol Documentation](XModem/README.md)
- [Error Correction Documentation](ErrorCorrection/README.md)
- [Analog-Digital Conversion Documentation](AnalogDigitalConversion/README.md)
- [Huffman Encoding Documentation](HuffmanEncoding/README.md)

## License

This project is licensed under the MIT License.