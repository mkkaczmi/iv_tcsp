# Stałe definiujące wymiary macierzy H:
H_ROWS = 9           # Liczba wierszy macierzy H; odpowiada liczbie bitów parzystości, które są dodawane do wiadomości.
H_COLUMNS = 17       # Liczba kolumn macierzy H; jest równa liczbie bitów oryginalnych (8) plus bitów parzystości (9).

# Macierz H (9x17) używana do kodowania i dekodowania wiadomości. Każdy wiersz w macierzy reprezentuje równanie do obliczenia bitu parzystości.
H = [
    [1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

# Oblicza bit parzystości dla wiersza 'r' macierzy H na podstawie wiadomości 'msg'.
def get_parity_bit(msg, r):
    total = 0  # Inicjalizacja sumy
    for j in range(len(msg)):
        total += H[r][j] * msg[j]  # Mnoży element macierzy przez odpowiadający bit wiadomości
    return total % 2  # Zwraca bit parzystości (reszta z dzielenia przez 2)

# Dodaje do listy 'msg' bity parzystości obliczone przy użyciu macierzy H.
def add_parity_bits(msg):
    if len(msg) == 0:
        return  # Brak operacji przy pustej wiadomości
    for r in range(H_ROWS):
        parity_bit = get_parity_bit(msg, r)  # Oblicza bit parzystości dla wiersza 'r'
        msg.append(parity_bit)     # Dołącza bit parzystości do wiadomości

# Zamienia ciąg bitów (np. "01010101") w listę liczb, dodaje bity parzystości (funkcja kodowanie) i zwraca wynik jako string.
def encode_chunk(chunk_str):
    # Konwersja ciągu znaków na listę liczb całkowitych (bitów)
    bits = [int(b) for b in chunk_str]
    add_parity_bits(bits)  # Dodanie bitów parzystości do listy bitów
    # Łączenie listy bitów w jeden ciąg znaków i zwrócenie rezultatu
    return "".join(str(bit) for bit in bits)

# Oblicza syndrom błędu poprzez sumowanie bitów wiadomości pomnożonych przez elementy macierzy H, a następnie dzielenie modulo 2.
def calculate_syndrome(msg):
    errors = []  # Lista na przechowanie bitów syndromu błędu
    for i in range(H_ROWS):
        row_sum  = 0  # Inicjalizacja sumy dla wiersza 'i'
        for j in range(H_COLUMNS):
            # Obliczenie iloczynu i dodanie do sumy
            row_sum  += H[i][j] * msg[j]
        errors.append(row_sum  % 2)  # Dodanie wyniku modulo 2 do listy błędów
    return errors  # Zwraca syndrom błędu jako listę bitów

# Naprawia błędy w 'msg' według 'error': szuka kolumny, której pojedyncze odwrócenie bitu da zgodny syndrom.
def fix_error(msg, error):
    # Przeszukiwanie kolumn w poszukiwaniu pojedynczego błędu
    for i in range(H_COLUMNS):
        match = True  # Założenie zgodności kolumny z 'error'
        for j in range(H_ROWS):
            if H[j][i] != error[j]:
                match = False  # Jeśli którakolwiek wartość nie pasuje, kończymy sprawdzanie tej kolumny
                break
        if match:
            msg[i] ^= 1  # Odwrócenie bitu (operacja XOR z 1) w pozycji i
            return      # Wyjście z funkcji po korekcji błędu

    # Jeśli pojedyncza korekcja nie działa, szuka pary bitów, których odwrócenie daje poprawny syndrom.
    for i in range(H_COLUMNS):
        for j in range(i, H_COLUMNS):
            match = True  # Zakładamy zgodność pary bitów
            for k in range(H_ROWS):
                # Sprawdza, czy XOR bitów z kolumn i oraz j odpowiada k-temu bitowi syndromu.
                if (H[k][i] ^ H[k][j]) != error[k]:
                    match = False
                    break
            if match:
                msg[i] ^= 1  # Odwrócenie bitu w kolumnie i
                msg[j] ^= 1  # Odwrócenie bitu w kolumnie j
                return      # Kończy funkcję po dokonanej korekcji

# Oblicza syndrom błędu. Następnie koryguje błędy funkcją 'popraw' i zwraca pierwsze 8 bitów jako oryginalne dane.
def decode_chunk(encoded_chunk):
    errors = calculate_syndrome(encoded_chunk)    # Oblicza syndrom błędu
    fix_error(encoded_chunk, errors)      # Koryguje błędy
    return encoded_chunk[:8]           # Zwraca 8-bitowe dane

# Odczytuje zawartość pliku "input.txt" i przekształca każdy znak na postać binarną (8 bitów), koduje go (dodając bity parzystości), a następnie zapisuje wynik do pliku "encoded.txt".
def encode_text():
    try:
        with open("input.txt", "r", encoding="utf-8") as file_in:
            plain_text = file_in.read().rstrip("\n")  # Wczytaj tekst i usuń ostatnią nową linię
    except Exception as e:
        print("Błąd podczas czytania pliku input.txt:", e)
        return

    encoded_chunks = []  # Lista na zakodowane fragmenty
    for ch in plain_text:
        bit_str = format(ord(ch), "08b")        # Zamień znak na 8-bitowy kod ASCII
        encoded_chunk = encode_chunk(bit_str)   # Zakoduj (dodaj bity parzystości)
        encoded_chunks.append(encoded_chunk)

    encoded_message = "\n".join(encoded_chunks) # Połącz fragmenty w komunikat, każdy w nowej linii
    try:
        with open("encoded.txt", "w", encoding="utf-8") as file_encoded:
            file_encoded.write(encoded_message)     # Zapis do pliku
    except Exception as e:
        print("Błąd podczas zapisywania pliku encoded.txt:", e)
        return

    print("Kodowanie zakończone. Wynik zapisany w pliku encoded.txt.")


# Wczytuje "encoded.txt", dekoduje linie z korekcją błędów i zapisuje wynik do "decoded.txt".
def decode_text():
    try:
        with open("encoded.txt", "r", encoding="utf-8") as file_encoded:
            encoded_lines = file_encoded.read().splitlines()    # Wczytaj linie z pliku
    except Exception as e:
        print("Błąd podczas czytania pliku encoded.txt:", e)
        return

    decoded_chars = []  # Lista na zdekodowane znaki
    for idx, line in enumerate(encoded_lines):
        line = line.strip()  # Usuń zbędne spacje
        if len(line) == 0:
            continue  # Pomijanie pustych linii
        if len(line) != H_COLUMNS:
            # Jeżeli linia nie zawiera oczekiwanej liczby bitów, zgłaszamy błąd
            print(f"Błąd: Linia {idx+1} w pliku encoded.txt nie zawiera {H_COLUMNS} bitów.")
            return
        chunk = [int(b) for b in line]  # Zamień ciąg bitów na listę liczb
        original_bits = decode_chunk(chunk) # Dekoduj fragment, naprawiając błędy
        char_code = int("".join(str(b) for b in original_bits), 2)  # Zamień bity na kod ASCII
        decoded_chars.append(chr(char_code))    # Konwertuj kod na znak

    decoded_message = "".join(decoded_chars)    # Złącz znaki w wiadomość
    try:
        with open("decoded.txt", "w", encoding="utf-8") as file_decoded:
            file_decoded.write(decoded_message) # Zapisz wynik do pliku
    except Exception as e:
        print("Błąd podczas zapisywania pliku decoded.txt:", e)
        return

    print("Dekodowanie zakończone. Wynik zapisany w pliku decoded.txt.")

def main():
    mode = input("Wybierz tryb działania (encode/decode): ").strip().lower()
    if mode == "encode":
        encode_text()
    elif mode == "decode":
        decode_text()
    else:
        print("Nieprawidłowy tryb. Użyj 'encode' lub 'decode'.")

if __name__ == "__main__":
    main()
