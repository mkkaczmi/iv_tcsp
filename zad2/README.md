# XMODEM File Transfer

This script implements the XMODEM protocol for file transfer using serial communication. It supports both simple checksum and CRC (Cyclic Redundancy Check) for error checking.

## Features
- **Transmitter and Receiver**: The script can function as both a transmitter and a receiver.
- **Error Checking**: Supports both algebraic checksum and CRC for error detection.

## Requirements
- Python 3
- `pyserial` library

## Installation
Install the required library using pip:
```bash
pip install pyserial
```

## Usage
1. **Run the Script**: Execute the script using Python.
   ```bash
   python xmodem.py
   ```

2. **Select COM Port**: Choose the appropriate COM port for communication.

3. **Select Mode**:
   - `0`: Transmitter (send a file)
   - `1`: Receiver (receive a file)

4. **Select Checksum Mode**:
   - `0`: Simple checksum
   - `1`: CRC

5. **File Path**:
   - If transmitting, provide the path to the file to send.
   - If receiving, provide the name for the received file.

## Notes
- Ensure both the transmitter and receiver are using the same settings and are connected to the correct COM ports.
- The script will wait for the appropriate signals to synchronize before starting the file transfer.