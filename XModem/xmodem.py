import serial  # Import biblioteki do komunikacji szeregowej (RS-232)

# Definicje znaków sterujących zgodnych z protokołem XMODEM
SOH = 0x01  # Start of Header – początek bloku danych
EOT = 0x04  # End of Transmission – koniec transmisji
ACK = 0x06  # Acknowledge – potwierdzenie poprawnego odbioru
NAK = 0x15  # Negative Acknowledge – negacja, błąd w odbiorze
CAN = 0x18  # Cancel – przerwanie transmisji
CRC_MODE = 0x43  # 'C' – żądanie użycia CRC zamiast sumy kontrolnej

BLOCK_SIZE = 128  # Rozmiar bloku danych zgodny z protokołem XMODEM

# Funkcja obliczająca CRC-16 dla danych wejściowych
def calc_crc(data):
    crc = 0
    for b in data:
        crc ^= b << 8  # XOR z przesunięciem bajtu
        for _ in range(8):  # Dla każdego bitu
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021  # Maska CRC-16-CCITT
            else:
                crc <<= 1
        crc &= 0xFFFF  # Maskowanie do 16 bitów
    return crc.to_bytes(2, 'big')  # Zwraca CRC jako dwa bajty w kolejności big endian

# Klasa nadawcy pliku
class Transmitter:
    def __init__(self, serial_port):
        self.ser = serial_port  # Inicjalizacja portu szeregowego

    # Metoda do wysyłania pliku przez port szeregowy z opcjonalnym trybem CRC
    def send_file(self, data, crc_mode):
        block_number = 1  # Numer pierwszego bloku
        offset = 0  # Pozycja odczytu danych
        while True:  # Oczekiwanie na rozpoczęcie transmisji
            ch = self.ser.read(1)  # Odczytaj jeden bajt z portu
            if ch:
                if crc_mode and ch[0] == CRC_MODE:  # Jeśli tryb CRC i odebrano 'C'
                    break
                elif not crc_mode and ch[0] == NAK:  # Jeśli zwykły tryb i odebrano NAK
                    break

        while offset < len(data):  # Dopóki nie wysłano wszystkich danych
            block = data[offset:offset + BLOCK_SIZE]  # Wyodrębnij blok danych
            if len(block) < BLOCK_SIZE:  # Uzupełnienie do pełnego bloku (padding)
                block += bytes([0x1A] * (BLOCK_SIZE - len(block)))  # 0x1A = ASCII SUB

            # Tworzenie pakietu: SOH + nr bloku + jego uzupełnienie + dane
            packet = bytes([SOH, block_number, 255 - block_number]) + block
            if crc_mode:
                crc = calc_crc(block)  # Oblicz CRC dla bloku
                packet += crc  # Dodaj CRC do pakietu
            else:
                checksum = sum(block) % 256  # Oblicz sumę kontrolną
                packet += bytes([checksum])  # Dodaj sumę do pakietu

            self.ser.write(packet)  # Wyślij pakiet przez port
            response = self.ser.read(1)  # Oczekuj na odpowiedź
            if not response or response[0] != ACK:  # Jeśli brak ACK – przerwij transmisję
                print("Blad transmisji, przerwano.")
                self.ser.write(bytes([CAN]))
                return
            offset += BLOCK_SIZE  # Przesuń offset o rozmiar bloku
            block_number = (block_number + 1) % 256  # Zwiększ numer bloku

        self.ser.write(bytes([EOT]))  # Wyślij znak końca transmisji
        while True:
            ack = self.ser.read(1)  # Czekaj na potwierdzenie ACK
            if ack == bytes([ACK]):
                break

# Klasa odbiorcy pliku
class Receiver:
    def __init__(self, serial_port):
        self.ser = serial_port  # Inicjalizacja portu

    # Metoda odbierająca plik w wybranym trybie sumy kontrolnej lub CRC
    def receive_file(self, crc_mode):
        self.ser.write(bytes([CRC_MODE if crc_mode else NAK]))  # Rozpoczęcie transmisji
        block_number = 1
        result = bytearray()

        while True:
            soh = self.ser.read(1)  # Odczytaj znak rozpoczęcia
            if not soh:
                continue
            if soh[0] == EOT:  # Koniec transmisji
                self.ser.write(bytes([ACK]))
                break
            if soh[0] != SOH:  # Pominięcie błędnych pakietów
                continue

            header = self.ser.read(2)  # Odczytaj nagłówek: numer bloku i jego uzupełnienie
            block = self.ser.read(BLOCK_SIZE)  # Odczytaj dane
            trailer = self.ser.read(2 if crc_mode else 1)  # Odczytaj CRC lub sumę

            if len(header) < 2 or len(block) < BLOCK_SIZE:  # Błąd w długości – NAK
                self.ser.write(bytes([NAK]))
                continue

            blk_num, blk_comp = header
            if blk_num != block_number or blk_comp != (255 - blk_num):  # Weryfikacja numeru
                self.ser.write(bytes([NAK]))
                continue

            if crc_mode:
                expected_crc = calc_crc(block)
                if trailer != expected_crc:  # Sprawdzenie poprawności CRC
                    self.ser.write(bytes([NAK]))
                    continue
            else:
                checksum = sum(block) % 256
                if trailer[0] != checksum:  # Sprawdzenie sumy kontrolnej
                    self.ser.write(bytes([NAK]))
                    continue

            result.extend(block)  # Dodaj poprawny blok do wyniku
            self.ser.write(bytes([ACK]))  # Potwierdź odbiór
            block_number = (block_number + 1) % 256  # Zwiększ numer bloku

        return result.rstrip(b'\x1A')  # Usuń znaki paddingu (SUB)

def main():
    print("Dostępne porty: COM1, COM2")
    port = input("Wybierz port COM: ").strip().upper()
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)  # Otwarcie portu
    except serial.SerialException:
        print(f"Nie można otworzyć portu {port}")
        return

    print("Wybierz tryb pracy:\n0) wysylanie\n1) odbieranie")
    working_mode = int(input())
    print("Wybierz tryb sumy kontrolnej:\n0) suma kontrolna\n1) CRC")
    checksum_mode = int(input())

    if working_mode not in [0, 1] or checksum_mode not in [0, 1]:  # Walidacja wejścia
        print("Niepoprawne parametry!")
        return

    if working_mode == 0:
        filename = input("Podaj sciezke do pliku: ")
        with open(filename, 'rb') as f:
            data = f.read()
        tr = Transmitter(ser)
        tr.send_file(data, checksum_mode)  # Rozpocznij wysyłanie

    elif working_mode == 1:  # Tryb odbioru
        filename = input("Podaj nazwe pliku do odebrania: ")
        re = Receiver(ser)
        data = re.receive_file(checksum_mode)  # Rozpocznij odbieranie
        with open(filename, 'wb') as f:
            f.write(data)

if __name__ == "__main__":
    main()