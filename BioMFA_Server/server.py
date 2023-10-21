import asyncio
import websockets
import json
import sqlite3
import random
import redis

# Połączenie z bazą SQLite (User)
sqlite_conn = sqlite3.connect('users.db')
sqlite_cursor = sqlite_conn.cursor()

# Połączenie z Redis (Operation)
redis_conn = redis.StrictRedis(host='192.168.6.146', port=20646, db=0)

# Funkcja obsługująca rejestrację użytkownika
async def register_user(username, password, websocket):
    # Zapisz dane użytkownika w bazie Operation (Redis)
    operation_id = generate_operation_id()
    operation_data = {
        "username": username,
        "password": password,
        "web_addr": websocket.remote_address[0]
    }
    redis_conn.hset("Operation", operation_id, json.dumps(operation_data))

    # Odpowiedz z ID operacji
    response = {
        "action": "REGISTER",
        "sender": "Server",
        "content": {
            "operation_id": operation_id
        }
    }
    await websocket.send(json.dumps(response))

# Funkcja obsługująca logowanie użytkownika
async def login_user(username, password, websocket):
    # Weryfikacja hasła w bazie danych SQLite (User)
    sqlite_cursor.execute("SELECT username, password FROM User WHERE username=?", (username,))
    user_data = sqlite_cursor.fetchone()

    if user_data is None or user_data[1] != password:
        # Wysłanie komunikatu o błędzie logowania
        response = {
            "action": "LOGIN",
            "sender": "Server",
            "content": "Invalid credentials"
        }
        await websocket.send(json.dumps(response))
    else:
        # Logowanie udane, generowanie ID operacji
        operation_id = generate_operation_id()
        operation_data = {
            "username": username,
            "web_addr": websocket.remote_address[0]
        }
        redis_conn.hset("Operation", operation_id, json.dumps(operation_data))

        # Odpowiedz z ID operacji
        response = {
            "action": "LOGIN",
            "sender": "Server",
            "content": {
                "operation_id": operation_id
            }
        }
        await websocket.send(json.dumps(response))

# Funkcja generująca unikalne ID operacji
def generate_operation_id():
    return str(random.randint(100000, 999999))

async def handle_client(websocket, path):
    async for message in websocket:
        message_data = json.loads(message)
        action = message_data.get("action")
        sender = message_data.get("sender")
        content = message_data.get("content")

        if action == "REGISTER" and sender == "Web":
            username = content.get("username")
            password = content.get("password")

            await register_user(username, password, websocket)

        elif action == "LOGIN" and sender == "Web":
            username = content.get("username")
            password = content.get("password")

            await login_user(username, password, websocket)

        elif action == "REGISTER" and sender == "Mobile":
            operation_id = content.get("operation_id")
            mfa_id = content.get("mfa_id")

            # Obsłuż rejestrację użytkownika z aplikacji mobilnej
            # Dopisz mfa_id do odpowiedniego rekordu w bazie Operation
            operation_data = json.loads(redis_conn.hget("Operation", operation_id))
            operation_data["mfa_id"] = mfa_id
            redis_conn.hset("Operation", operation_id, json.dumps(operation_data))

            # Odczytaj adres Web, na który należy przesłać komunikat sukcesu
            web_addr = operation_data.get("web_addr")
            web_socket = await websockets.connect(f"ws://{web_addr}")
            success_message = {
                "action": "REGISTER",
                "sender": "Server",
                "content": "Registration successful"
            }
            await web_socket.send(json.dumps(success_message))

            # Przenieś rekord Operation do bazy User, zatwierdzając użytkownika
            user_data = {
                "username": operation_data["username"],
                "password": operation_data["password"],
                "mfa_id": operation_data["mfa_id"]
            }
            sqlite_cursor.execute("INSERT INTO User (username, password, mfa_id) VALUES (?, ?, ?)",
                                  (user_data["username"], user_data["password"], user_data["mfa_id"]))
            sqlite_conn.commit()

        elif action == "LOGIN" and sender == "Mobile":
            operation_id = content.get("operation_id")
            mfa_id = content.get("mfa_id")

            # Sprawdź, czy ID operacji istnieje w bazie Operation
            if redis_conn.hexists("Operation", operation_id):
                operation_data = json.loads(redis_conn.hget("Operation", operation_id))

                # Sprawdź poprawność MFA ID w bazie User
                if operation_data.get("mfa_id") == mfa_id:
                    # Odczytaj adres Web
                    web_addr = operation_data.get("web_addr")

                    # Odpowiedz wynikiem operacji na odczytany adres Web
                    web_socket = await websockets.connect(f"ws://{web_addr}")
                    success_message = {
                        "action": "LOGIN",
                        "sender": "Server",
                        "content": "Login successful"
                    }
                    await web_socket.send(json.dumps(success_message))
                else:
                    # Odpowiedz błędem autoryzacji MFA
                    failure_message = {
                        "action": "LOGIN",
                        "sender": "Server",
                        "content": "MFA authentication failed"
                    }
                    await websocket.send(json.dumps(failure_message))
            else:
                # Odpowiedz błędem braku operacji
                failure_message = {
                    "action": "LOGIN",
                    "sender": "Server",
                    "content": "Operation not found"
                }
                await websocket.send(json.dumps(failure_message))

start_server = websockets.serve(handle_client, "192.168.6.146", 20646)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

