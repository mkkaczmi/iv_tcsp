# Huffman Encoding Module

This module implements the Huffman coding algorithm for data compression and demonstrates its usage in a client-server architecture for text compression and transmission.

## Features

- Huffman tree construction and encoding
- Text compression using variable-length codes
- Client-server implementation for data transmission
- Compression ratio calculation
- Support for UTF-8 text encoding
- Binary data handling with padding

## Requirements

- Python 3.x
- bitarray

## Installation

Install the required dependency:
```bash
pip install bitarray
```

## Usage

The program can be run in two modes: server and client.

### Server Mode

Run the server to receive and decode compressed text:
```bash
python main.py server
```

The server will:
1. Listen for incoming connections
2. Receive compressed data and Huffman codes
3. Decode the received data
4. Save the decoded text to `decoded.txt`

### Client Mode

Run the client to compress and send text:
```bash
python main.py client input.txt
```

The client will:
1. Read the input text file
2. Build Huffman codes for the text
3. Compress the text using the generated codes
4. Send the compressed data and codes to the server
5. Save the Huffman codes to `huffman_codes.json`

## Output Files

The program generates the following files:
- `huffman_codes.json`: Dictionary of Huffman codes for each character
- `decoded.txt`: Decoded text received by the server

## Compression Analysis

The program displays:
- Huffman codes for each character
- Compression ratio
- Original and compressed data sizes

## Implementation Details

- Uses bitarray for efficient bit-level operations
- Implements padding for byte-aligned transmission
- Handles UTF-8 encoded text
- Provides error handling for network operations