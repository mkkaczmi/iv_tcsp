import serial
import struct
import os
from typing import Optional

# Constants
SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15
C = ord('C')
SUB = 26

class XMODEM:
    def __init__(self, port: str, baudrate: int = 9600):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.timeout = 1
        self.crc = False

    def open(self):
        try:
            self.serial.open()
            print(f"Successfully opened port {self.serial.port}")
        except serial.SerialException as e:
            print(f"Error opening port {self.serial.port}: {str(e)}")
            print("Please check if:")
            print("1. The port exists")
            print("2. The port is not in use by another program")
            print("3. You have the necessary permissions")
            raise

    def close(self):
        self.serial.close()

    def send(self, data: bytes):
        self.serial.write(data)

    def receive(self, length: int) -> bytes:
        return self.serial.read(length)

    def crc16(self, data: bytes) -> int:
        crc = 0
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
        return crc & 0xFFFF

    def send_file(self, filename: str):
        if not os.path.exists(filename):
            print(f"File {filename} does not exist")
            return

        print("Waiting for receiver to respond...")
        print("Make sure the receiver is:")
        print("1. Running and in receive mode")
        print("2. Connected to the same COM port")
        print("3. Using the same baud rate (9600)")

        # Wait for receiver's response
        response = self.receive(1)
        if not response:  # No data received
            print("No response from receiver after 1 second timeout")
            print("Please check the connection and try again")
            return
            
        if response[0] == NAK:
            self.crc = False
            print("Receiver requested checksum mode")
        elif response[0] == C:
            self.crc = True
            print("Receiver requested CRC mode")
        else:
            print(f"Invalid response from receiver: {response[0]}")
            return

        print("Starting file transfer...")
        packet_number = 1
        with open(filename, 'rb') as f:
            while True:
                data = f.read(128)
                if not data:
                    break

                # Pad with SUB if needed
                if len(data) < 128:
                    data = data + bytes([SUB] * (128 - len(data)))

                # Calculate checksum
                if self.crc:
                    checksum = self.crc16(data)
                else:
                    checksum = sum(data) % 256

                # Send packet
                header = bytes([SOH, packet_number, 255 - packet_number])
                self.send(header)
                self.send(data)
                if self.crc:
                    self.send(struct.pack('>H', checksum))
                else:
                    self.send(bytes([checksum]))

                # Wait for ACK
                response = self.receive(1)
                if not response:  # No response received
                    print("No response from receiver, retrying...")
                    f.seek(-128, 1)  # Rewind
                    continue
                    
                if response[0] != ACK:
                    print("Received NAK, retrying packet...")
                    f.seek(-128, 1)  # Rewind if NAK received
                else:
                    print(f"Packet {packet_number} sent successfully")
                    packet_number = (packet_number + 1) % 256

        print("File transfer complete, sending EOT...")
        # Send EOT
        while True:
            self.send(bytes([EOT]))
            response = self.receive(1)
            if not response:  # No response received
                print("No response from receiver, retrying EOT...")
                continue
                
            if response[0] == ACK:
                print("Transfer completed successfully!")
                break

    def receive_file(self, filename: str):
        # Send initial NAK or C
        self.send(bytes([C if self.crc else NAK]))

        with open(filename, 'wb') as f:
            while True:
                # Receive header
                header = self.receive(1)
                if not header:  # No data received
                    continue
                    
                if header[0] == EOT:
                    self.send(bytes([ACK]))
                    break

                if header[0] != SOH:
                    continue

                # Receive packet number and complement
                packet_info = self.receive(2)
                if len(packet_info) != 2:  # Not enough data received
                    self.send(bytes([NAK]))
                    continue
                    
                packet_number = packet_info[0]
                complement = packet_info[1]

                if packet_number + complement != 255:
                    self.send(bytes([NAK]))
                    continue

                # Receive data
                data = self.receive(128)
                if len(data) != 128:  # Not enough data received
                    self.send(bytes([NAK]))
                    continue

                # Receive checksum
                if self.crc:
                    checksum_data = self.receive(2)
                    if len(checksum_data) != 2:
                        self.send(bytes([NAK]))
                        continue
                    checksum = struct.unpack('>H', checksum_data)[0]
                    calculated_checksum = self.crc16(data)
                else:
                    checksum_data = self.receive(1)
                    if len(checksum_data) != 1:
                        self.send(bytes([NAK]))
                        continue
                    checksum = checksum_data[0]
                    calculated_checksum = sum(data) % 256

                if checksum != calculated_checksum:
                    self.send(bytes([NAK]))
                    continue

                # Write data to file
                if packet_number == 1:  # First packet
                    f.write(data)
                else:
                    # Find last non-SUB byte
                    last_byte = 127
                    while last_byte >= 0 and data[last_byte] == SUB:
                        last_byte -= 1
                    f.write(data[:last_byte + 1])

                self.send(bytes([ACK]))

def main():
    print("Authors:\nKamil Kowalewski 216806\nJakub Plich 216866\n")

    # Choose mode
    while True:
        print("Choose mode:\n1. Send\n2. Receive\nChoice: ", end='')
        try:
            choice = int(input())
            if choice in (1, 2):
                break
        except ValueError:
            pass

    # File name
    filename = "coded2.txt"

    # Choose port
    while True:
        print("Choose port:\n1. COM1\n2. COM2\n3. COM3\n4. COM4\nChoice: ", end='')
        try:
            port_number = int(input())
            if port_number in (1, 2, 3, 4):
                break
        except ValueError:
            pass

    port = f"COM{port_number}"

    # Choose CRC
    while True:
        print("Enable CRC:\n1. Yes\n2. No\nChoice: ", end='')
        try:
            crc_choice = int(input())
            if crc_choice in (1, 2):
                break
        except ValueError:
            pass

    # Initialize XMODEM
    xmodem = XMODEM(port)
    xmodem.crc = (crc_choice == 1)
    xmodem.open()

    try:
        if choice == 1:
            xmodem.send_file(filename)
        else:
            xmodem.receive_file(filename)
    finally:
        xmodem.close()

if __name__ == "__main__":
    main() 