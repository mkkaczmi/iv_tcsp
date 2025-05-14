import json
import socket
import sys
from collections import Counter
from bitarray import bitarray
from typing import Dict, Tuple

class HuffmanNode:
    # Prosty węzeł drzewa Huffmana
    def __init__(self, char, frequency):
        self.char = char  # znak przechowywany w węźle (None dla węzłów wewnętrznych)
        self.frequency = frequency  # częstość występowania znaku
        self.left = None  # lewe dziecko
        self.right = None  # prawe dziecko
    
    def is_leaf(self):
        # Sprawdza czy węzeł jest liściem (przechowuje znak)
        return self.char is not None

def build_tree(text):
    # Buduje drzewo Huffmana dla podanego tekstu
    
    # Zlicz częstość występowania każdego znaku
    frequencies = Counter(text)
    
    # Utwórz listę węzłów dla każdego znaku
    nodes = []
    for char, freq in frequencies.items():
        nodes.append(HuffmanNode(char, freq))
    
    # Buduj drzewo, łącząc węzły o najmniejszej częstości
    while len(nodes) > 1:
        # Sortuj węzły po częstości
        nodes = sorted(nodes, key=lambda x: x.frequency)
        
        # Pobierz dwa węzły o najmniejszej częstości
        left = nodes.pop(0)
        right = nodes.pop(0)
        
        # Utwórz nowy węzeł wewnętrzny
        internal = HuffmanNode(None, left.frequency + right.frequency)
        internal.left = left
        internal.right = right
        
        # Dodaj nowy węzeł do listy
        nodes.append(internal)
    
    # Zwróć korzeń drzewa
    return nodes[0]

def create_codes(root, current_code=None, codes=None):
    # Tworzy słownik kodów Huffmana dla każdego znaku używając bitarray
    if current_code is None:
        current_code = bitarray()
    if codes is None:
        codes = {}
    
    # Jeśli węzeł jest liściem, zapisz jego kod
    if root.is_leaf():
        if len(current_code) == 0:
            codes[root.char] = bitarray('0')
        else:
            codes[root.char] = current_code.copy()
        return codes
    
    # Rekurencyjnie przejdź przez drzewo
    if root.left:
        current_code.append(0)
        create_codes(root.left, current_code, codes)
        current_code.pop()
    if root.right:
        current_code.append(1)
        create_codes(root.right, current_code, codes)
        current_code.pop()
    
    return codes

def encode(text, codes):
    # Koduje tekst używając słownika kodów Huffmana
    result = bitarray()
    for char in text:
        result.extend(codes[char])
    return result

def decode_with_codes(encoded_bits, codes):
    # Dekoduje dane binarne używając słownika kodów Huffmana
    if not encoded_bits:
        return ""
    
    # Odwróć słownik kodów (kod -> znak) i przekonwertuj klucze na bitarray
    reverse_codes = {code.to01(): char for char, code in codes.items()}
    
    result = []
    current_code = bitarray()
    
    # Przejdź przez zakodowane dane bit po bicie
    for bit in encoded_bits:
        current_code.append(bit)
        current_str = current_code.to01()
        if current_str in reverse_codes:
            result.append(reverse_codes[current_str])
            current_code = bitarray()
    
    return "".join(result)

def prepare_data_for_sending(encoded_bits, codes):
    # Przygotowuje dane do wysłania przez sieć
    # Konwertuje bitarray na bytes i przygotowuje słownik kodów do serializacji
    
    # Konwertuj kody bitarray na stringi dla JSON
    codes_for_json = {char: code.to01() for char, code in codes.items()}
    
    # Oblicz długość ostatniego bajtu w bitach (potrzebne przy dekodowaniu)
    padding_length = (8 - (len(encoded_bits) % 8)) % 8
    
    # Dodaj padding do encoded_bits
    encoded_bits_padded = encoded_bits.copy()
    encoded_bits_padded.extend([0] * padding_length)
    
    return (
        encoded_bits_padded.tobytes(),  # dane binarne
        {
            'codes': codes_for_json,
            'padding_length': padding_length
        }
    )

def run_server(port=12345):
    # Uruchamia serwer, który odbiera i dekoduje tekst
    print(f"Uruchamiam serwer na porcie {port}...")
    
    # Utwórz gniazdo serwera
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    
    try:
        # Czekaj na połączenie
        client_socket, address = server_socket.accept()
        print(f"Połączono z {address}")
        
        # Najpierw odbierz metadane (jako JSON)
        metadata_size = int.from_bytes(client_socket.recv(4), byteorder='big')
        metadata_json = client_socket.recv(metadata_size).decode()
        metadata = json.loads(metadata_json)
        
        # Następnie odbierz dane binarne
        data_size = int.from_bytes(client_socket.recv(4), byteorder='big')
        binary_data = client_socket.recv(data_size)
        
        # Konwertuj odebrane dane na bitarray
        received_bits = bitarray()
        received_bits.frombytes(binary_data)
        
        # Usuń padding
        if metadata['padding_length'] > 0:
            received_bits = received_bits[:-metadata['padding_length']]
        
        # Konwertuj kody ze stringów z powrotem na bitarray
        codes = {char: bitarray(code_str) for char, code_str in metadata['codes'].items()}
        
        # Dekoduj tekst
        decoded = decode_with_codes(received_bits, codes)
        
        # Zapisz wynik
        with open('decoded.txt', 'w', encoding='utf-8') as f:
            f.write(decoded)
        
        print("Tekst został zdekodowany i zapisany do pliku decoded.txt")
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        client_socket.close()
        server_socket.close()

def run_client(input_file, port=12345):
    # Uruchamia klienta, który koduje i wysyła tekst
    try:
        # Wczytaj tekst z pliku
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Zbuduj drzewo i utwórz kody
        root = build_tree(text)
        codes = create_codes(root)
        
        # Wyświetl kody dla każdego znaku
        print("\nKody Huffmana:")
        for char, code in codes.items():
            print(f"'{char}': {code.to01()}")
        
        # Zapisz słownik kodowy do pliku (dla referencji)
        codes_for_json = {char: code.to01() for char, code in codes.items()}
        with open('huffman_codes.json', 'w', encoding='utf-8') as f:
            json.dump(codes_for_json, f, ensure_ascii=False, indent=2)
        
        # Zakoduj tekst do postaci binarnej
        encoded_bits = encode(text, codes)
        compression_ratio = len(text) * 8 / len(encoded_bits)
        print(f"\nStopień kompresji: {compression_ratio:.2f}x")
        
        # Przygotuj dane do wysłania
        binary_data, metadata = prepare_data_for_sending(encoded_bits, codes)
        
        # Konwertuj metadane na JSON
        metadata_json = json.dumps(metadata).encode()
        
        # Wyślij dane
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', port))
        
        # Wyślij najpierw metadane (poprzedzone ich rozmiarem)
        client_socket.send(len(metadata_json).to_bytes(4, byteorder='big'))
        client_socket.send(metadata_json)
        
        # Następnie wyślij dane binarne (poprzedzone ich rozmiarem)
        client_socket.send(len(binary_data).to_bytes(4, byteorder='big'))
        client_socket.send(binary_data)
        
        print(f"\nDane zostały wysłane do serwera")
        print(f"Rozmiar oryginalny: {len(text)} bajtów")
        print(f"Rozmiar po kompresji: {len(binary_data)} bajtów")
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        client_socket.close()

def main():
    # Główna funkcja programu
    if len(sys.argv) < 2:
        print("Użycie:")
        print("  Serwer: python main.py server")
        print("  Klient: python main.py client plik.txt")
        return
    
    # Sprawdź tryb działania
    mode = sys.argv[1].lower()
    
    if mode == 'server':
        run_server()
    elif mode == 'client':
        if len(sys.argv) < 3:
            print("Błąd: Nie podano pliku wejściowego")
            return
        run_client(sys.argv[2])
    else:
        print("Nieznany tryb. Użyj 'server' lub 'client'")

if __name__ == "__main__":
    main()
