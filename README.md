# Error Correction Code Program

This program implements error-correcting codes for encoding and decoding binary data with error detection and correction capabilities. It uses a Hamming (12,8) code that can detect and correct single-bit errors.

## Features

- Encode any binary file using Hamming (12,8) code
- Decode encoded files with error correction
- Simulate transmission errors by introducing random bit flips
- Command-line interface for easy use
- Preserves case sensitivity in text files

## Requirements

- Python 3.x
- NumPy library

Install required packages:
```bash
pip install numpy
```

## Usage

### Basic Usage

1. Encode a file:
```bash
python error_correction.py encode input.txt encoded.bin
```

2. Decode a file:
```bash
python error_correction.py decode encoded.bin decoded.txt
```

### Introducing Errors

You can simulate transmission errors by introducing random bit flips during encoding:

1. Encode with one random error:
```bash
python error_correction.py encode input.txt encoded_with_1_error.bin --errors 1
```

2. Encode with two random errors:
```bash
python error_correction.py encode input.txt encoded_with_2_errors.bin --errors 2
```

### Command Line Arguments

- `mode`: Operation mode (`encode` or `decode`)
- `input_file`: Path to the input file
- `output_file`: Path to the output file
- `--errors`: Number of errors to introduce (0-2, default: 0)

## Example

1. Create a test file:
```bash
echo "Hello, this is a test message!" > test_input.txt
```

2. Encode the file:
```bash
python error_correction.py encode test_input.txt encoded.bin
```

3. Decode the file:
```bash
python error_correction.py decode encoded.bin decoded.txt
```

4. Compare the files:
```bash
diff test_input.txt decoded.txt
```

## Error Correction Details

The program uses a Hamming (12,8) code which:
- Takes 8 bits of data and adds 8 parity bits
- Can detect and correct single-bit errors
- Can detect double-bit errors but cannot correct them
- Uses a parity check matrix for error detection and correction

## Notes

- The program works with any binary file, not just text files
- When encoding text files, case sensitivity is preserved
- The encoded file will be approximately twice the size of the input file due to the added parity bits
- Error correction works best with single-bit errors; double-bit errors may not be corrected properly 