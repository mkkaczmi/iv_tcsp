#!/usr/bin/env python3

import argparse
import random
import numpy as np
from typing import List, Tuple

class ErrorCorrection:
    def __init__(self):
        # Hamming (12,8) parity check matrix
        self.H = np.array([
            [1,1,1,1,1,1,1,1, 1,0,0,0,0,0,0,0],
            [1,1,0,1,1,1,1,1, 0,1,0,0,0,0,0,0],
            [1,1,0,1,1,1,0,1, 0,0,1,0,0,0,0,0],
            [1,1,0,1,0,1,0,1, 0,0,0,1,0,0,0,0],
            [1,0,0,1,0,1,0,1, 0,0,0,0,1,0,0,0],
            [1,0,0,1,0,1,0,0, 0,0,0,0,0,1,0,0],
            [1,0,0,1,0,0,0,0, 0,0,0,0,0,0,1,0],
            [1,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,1]
        ])

    def byte_to_bits(self, byte: int) -> List[int]:
        """Convert a byte to a list of 8 bits."""
        return [int(b) for b in format(byte, '08b')]

    def bits_to_byte(self, bits: List[int]) -> int:
        """Convert a list of 8 bits to a byte."""
        return int(''.join(map(str, bits)), 2)

    def calculate_parity_bits(self, data_bits: List[int]) -> List[int]:
        """Calculate parity bits for Hamming (12,8) code."""
        parity_bits = []
        for i in range(8):  # 8 parity bits
            parity = 0
            # Calculate parity based on data bits
            for j in range(8):  # First 8 columns (data bits)
                if self.H[i][j] == 1:
                    parity ^= data_bits[j]
            # Calculate parity based on previously calculated parity bits
            for j in range(8, 16):  # Last 8 columns (parity bits)
                if self.H[i][j] == 1:
                    if j - 8 < len(parity_bits):
                        parity ^= parity_bits[j - 8]
            parity_bits.append(parity)
        return parity_bits

    def encode_byte(self, byte: int) -> List[int]:
        """Encode a single byte using Hamming (12,8) code."""
        data_bits = self.byte_to_bits(byte)
        parity_bits = self.calculate_parity_bits(data_bits)
        return data_bits + parity_bits

    def decode_byte(self, encoded_bits: List[int]) -> Tuple[int, bool]:
        """Decode a 16-bit codeword and correct single-bit errors."""
        syndrome = np.zeros(8, dtype=int)
        for i in range(8):
            for j in range(16):
                syndrome[i] ^= self.H[i][j] * encoded_bits[j]

        # Check for errors
        error_pos = -1
        for i in range(16):
            if np.array_equal(syndrome, self.H[:, i]):
                error_pos = i
                break

        # Correct error if found
        if error_pos != -1:
            encoded_bits[error_pos] ^= 1

        # Extract data bits (first 8 bits)
        data_bits = encoded_bits[:8]
        return self.bits_to_byte(data_bits), error_pos != -1

    def introduce_errors(self, encoded_data: List[int], num_errors: int) -> List[int]:
        """Introduce random bit errors in the encoded data."""
        result = encoded_data.copy()
        positions = random.sample(range(len(result)), num_errors)
        for pos in positions:
            result[pos] ^= 1
        return result

def process_file(input_file: str, output_file: str, mode: str, error_count: int = 0):
    """Process input file and save results to output file."""
    ec = ErrorCorrection()
    
    if mode == 'encode':
        with open(input_file, 'rb') as f_in, open(output_file, 'w') as f_out:
            while True:
                byte = f_in.read(1)
                if not byte:
                    break
                encoded = ec.encode_byte(byte[0])
                if error_count > 0:
                    encoded = ec.introduce_errors(encoded, error_count)
                # Convert encoded bits to string and write with newline
                encoded_str = ''.join(map(str, encoded))
                f_out.write(encoded_str + '\n')
    
    elif mode == 'decode':
        with open(input_file, 'r') as f_in, open(output_file, 'wb') as f_out:
            for line in f_in:
                # Remove newline and convert string to list of bits
                encoded_str = line.strip()
                if len(encoded_str) != 16:  # Skip invalid lines
                    continue
                encoded = [int(bit) for bit in encoded_str]
                decoded_byte, error_corrected = ec.decode_byte(encoded)
                f_out.write(bytes([decoded_byte]))

def main():
    parser = argparse.ArgumentParser(description='Error Correction Code Encoder/Decoder')
    parser.add_argument('mode', choices=['encode', 'decode'], help='Operation mode')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--errors', type=int, default=0, help='Number of errors to introduce (0-2)')
    
    args = parser.parse_args()
    
    if args.errors < 0 or args.errors > 2:
        print("Error count must be between 0 and 2")
        return
    
    process_file(args.input_file, args.output_file, args.mode, args.errors)
    print(f"Processing complete. Mode: {args.mode}, Errors introduced: {args.errors}")

if __name__ == '__main__':
    main() 