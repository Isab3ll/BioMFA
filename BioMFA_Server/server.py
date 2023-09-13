import socket
import random

# Adres i port serwera
HOST = '127.0.0.1'
PORT = 12345

# Słownik do przechowywania danych z operacji REGISTER
registered_data = {}

# A - BioMFA_Mobile, aplikacja mobilna w Kotlinie
# B - BioMFA_Web, aplikacja webowa w Pyhtonie

# Funkcja do generowania jednorazowego kodu ID operacji
def generate_operation_id():
    return str(random.randint(100000, 999999))

# Funkcja do obsługi operacji REGISTER od aplikacji B
def handle_register_from_B(client_socket):
    operation_id = generate_operation_id()
    client_socket.send(operation_id.encode())

# Funkcja do obsługi operacji REGISTER od aplikacji A
def handle_register_from_A(client_socket, operation_id, mfa_id):
    registered_data[operation_id] = mfa_id

# Funkcja do obsługi operacji LOGIN od aplikacji B
def handle_login_from_B(client_socket):
    operation_id = generate_operation_id()
    client_socket.send(operation_id.encode())

# Funkcja do obsługi operacji LOGIN od aplikacji A
def handle_login_from_A(client_socket, operation_id, mfa_id):
    if operation_id in registered_data and registered_data[operation_id] == mfa_id:
        client_socket.send("Login successful".encode())
    else:
        client_socket.send("Login failed".encode())

# Główna funkcja obsługująca serwer
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"Serwer nasłuchuje na {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                print(f"Połączono z {addr}")

                message = client_socket.recv(1024).decode()
                if message == "REGISTER":
                    handle_register_from_B(client_socket)
                elif message.startswith("REGISTER "):
                    _, operation_id, mfa_id = message.split()
                    handle_register_from_A(client_socket, operation_id, mfa_id)
                elif message == "LOGIN":
                    handle_login_from_B(client_socket)
                elif message.startswith("LOGIN "):
                    _, operation_id, mfa_id = message.split()
                    handle_login_from_A(client_socket, operation_id, mfa_id)

if __name__ == "__main__":
    main()
