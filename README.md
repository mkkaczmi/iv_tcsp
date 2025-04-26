# TCSP Project

This repository contains implementations of communication protocols and error correction mechanisms for serial communication.

## Project Structure

The project is organized into two main components:

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

## Requirements

- Python 3.x
- pyserial==3.5

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

## License

This project is licensed under the MIT License.