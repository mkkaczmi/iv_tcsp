import serial
import time
import sys

SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15
CAN = 0x18
CRC_MODE = 0x43  # 'C'

BLOCK_SIZE = 128

def calc_crc(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc.to_bytes(2, 'big')

class Transmitter:
    def __init__(self, serial_port):
        self.ser = serial_port

    def send_file(self, data, crc_mode):
        block_number = 1
        offset = 0
        if crc_mode:
            while True:
                ch = self.ser.read(1)
                if ch and ch[0] == CRC_MODE:
                    break

        while offset < len(data):
            block = data[offset:offset + BLOCK_SIZE]
            if len(block) < BLOCK_SIZE:
                block += bytes([0x1A] * (BLOCK_SIZE - len(block)))

            packet = bytes([SOH, block_number, 255 - block_number]) + block
            if crc_mode:
                crc = calc_crc(block)
                packet += crc
            else:
                checksum = sum(block) % 256
                packet += bytes([checksum])

            self.ser.write(packet)
            response = self.ser.read(1)
            if not response or response[0] != ACK:
                print("Blad transmisji, przerwano.")
                self.ser.write(bytes([CAN]))
                return
            offset += BLOCK_SIZE
            block_number = (block_number + 1) % 256

        self.ser.write(bytes([EOT]))
        while True:
            ack = self.ser.read(1)
            if ack == bytes([ACK]):
                break

class Receiver:
    def __init__(self, serial_port):
        self.ser = serial_port

    def receive_file(self, crc_mode):
        self.ser.write(bytes([CRC_MODE if crc_mode else NAK]))
        block_number = 1
        result = bytearray()

        while True:
            soh = self.ser.read(1)
            if not soh:
                continue
            if soh[0] == EOT:
                self.ser.write(bytes([ACK]))
                break
            if soh[0] != SOH:
                continue

            header = self.ser.read(2)
            block = self.ser.read(BLOCK_SIZE)
            trailer = self.ser.read(2 if crc_mode else 1)

            if len(header) < 2 or len(block) < BLOCK_SIZE:
                self.ser.write(bytes([NAK]))
                continue

            blk_num, blk_comp = header
            if blk_num != block_number or blk_comp != (255 - blk_num):
                self.ser.write(bytes([NAK]))
                continue

            if crc_mode:
                expected_crc = calc_crc(block)
                if trailer != expected_crc:
                    self.ser.write(bytes([NAK]))
                    continue
            else:
                checksum = sum(block) % 256
                if trailer[0] != checksum:
                    self.ser.write(bytes([NAK]))
                    continue

            result.extend(block)
            self.ser.write(bytes([ACK]))
            block_number = (block_number + 1) % 256

        return result.rstrip(b'\x1A')  # Strip padding

def main():
    print("Dostępne porty: COM1, COM2")
    port = input("Wybierz port COM: ").strip().upper()
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
    except serial.SerialException:
        print(f"Nie można otworzyć portu {port}")
        return

    print("Wybierz tryb pracy:\n0) wysylanie\n1) odbieranie")
    working_mode = int(input())
    print("Wybierz tryb sumy kontrolnej:\n0) suma kontrolna\n1) CRC")
    checksum_mode = int(input())

    if working_mode not in [0, 1] or checksum_mode not in [0, 1]:
        print("Niepoprawne parametry!")
        return

    if working_mode == 0:
        filename = input("Podaj sciezke do pliku: ")
        with open(filename, 'rb') as f:
            data = f.read()
        tr = Transmitter(ser)
        tr.send_file(data, checksum_mode)

    elif working_mode == 1:
        filename = input("Podaj nazwe pliku do odebrania: ")
        re = Receiver(ser)
        data = re.receive_file(checksum_mode)
        with open(filename, 'wb') as f:
            f.write(data)

if __name__ == "__main__":
    main()
