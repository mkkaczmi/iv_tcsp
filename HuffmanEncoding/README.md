# Huffman Coding Implementation

This project implements Huffman coding for text compression with client-server communication. It includes text compression using Huffman coding algorithm and network transmission of the compressed data.

## Features

- Text compression using Huffman coding
- Binary data transmission over network sockets
- Client-server architecture
- Compression ratio display
- Saving and loading Huffman codes
- Error handling and logging

## Requirements

- Python 3.x
- bitarray package

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd huffman-coding
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

The program can work in two modes: server and client.

### Starting the Server

Run the server first:
```bash
python main.py server
```

The server will:
- Listen for incoming connections
- Receive compressed data
- Decode the data using Huffman codes
- Save the decoded text to `decoded.txt`

### Running the Client

In a separate terminal, run the client with an input file:
```bash
python main.py client input.txt
```

The client will:
- Read the input text file
- Generate Huffman codes
- Display compression statistics
- Send the compressed data to the server
- Save the Huffman codes to `huffman_codes.json`

## Example

1. Create a text file `input.txt` with some content:
```
to be or not to be
```

2. Start the server in one terminal:
```bash
python main.py server
```

3. Run the client in another terminal:
```bash
python main.py client input.txt
```

4. Check the results:
- `decoded.txt` - contains the decoded text
- `huffman_codes.json` - contains the Huffman codes used for compression

## How It Works

1. **Huffman Tree Building**
   - Counts character frequencies in the input text
   - Builds a Huffman tree based on these frequencies
   - Generates optimal binary codes for each character

2. **Compression**
   - Converts text to binary data using Huffman codes
   - Efficiently packs bits into bytes for transmission
   - Includes necessary padding information

3. **Network Communication**
   - Uses TCP sockets for reliable data transmission
   - Sends metadata (Huffman codes) and compressed data separately
   - Handles data size prefixing for proper message framing

4. **Decompression**
   - Reconstructs binary data from received bytes
   - Uses Huffman codes to decode the original text
   - Handles padding removal

## File Structure

- `main.py` - Main program file containing all the code
- `requirements.txt` - List of Python package dependencies
- `README.md` - This documentation file
- Generated files:
  - `huffman_codes.json` - Generated Huffman codes
  - `decoded.txt` - Decoded output text

## Error Handling

The program includes error handling for common scenarios:
- File not found
- Network connection issues
- Invalid input data
- Decoding errors

## Performance

The compression ratio depends on the input text characteristics:
- More repetitive text = better compression
- Longer input text = more efficient compression
- Binary data transmission reduces network usage

## Limitations

- Works with text files only
- Both server and client must be running on the same machine (localhost)
- Fixed port number (12345)
- Single connection handling

## Contributing

Feel free to submit issues and enhancement requests!