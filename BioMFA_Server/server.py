import asyncio
import websockets
import json
import sqlite3
import random
import redis

# Połączenie z SQLite (baza danych User)
sqlite_conn = sqlite3.connect('users.db')
sqlite_cursor = sqlite_conn.cursor()

# Połączenie z Redis (baza danych Operation)
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

# Spis otwartych websocketów
ws = {}

# Funkcja obsługująca rejestrację użytkownika
async def register_user(username, password, websocket):
    # Wygeneruj ID operacji
    operation_id = generate_operation_id()
    # Zapisz websocket i ID operacji w bazie Operation
    ws[websocket.remote_address[0]] = websocket
    operation_data = {
        "username": username,
        "password": password,
        "web_addr": websocket.remote_address[0]
    }
    redis_conn.set(operation_id, json.dumps(operation_data))

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
    # Zweryfikuj hasło w bazie User
    sqlite_cursor.execute("SELECT username, password FROM User WHERE username=?", (username,))
    user_data = sqlite_cursor.fetchone()

    if user_data is None or user_data[1] != password:
        # Wyślij komunikat o błędzie logowania
        response = {
            "action": "LOGIN",
            "sender": "Server",
            "content": "Invalid credentials"
        }
        await websocket.send(json.dumps(response))
    else:
        # Logowanie udane, wygeneruj ID operacji
        operation_id = generate_operation_id()
        # Zapisz websocket i ID operacji w bazie Operation
        ws[websocket.remote_address[0]] = websocket
        operation_data = {
            "username": username,
            "web_addr": websocket.remote_address[0]
        }
        redis_conn.set(operation_id, json.dumps(operation_data))

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

# Funkcja obsługująca połączenie WebSocket
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

            # Dopisz mfa_id do odpowiedniego rekordu w bazie Operation
            operation_data = json.loads(redis_conn.get(operation_id))
            operation_data["mfa_id"] = mfa_id
            redis_conn.set(operation_id, json.dumps(operation_data))

            # Odczytaj odpowiedni adres i prześlij komunikat sukcesu
            web_addr = operation_data.get("web_addr")
            web_socket = ws[web_addr]
            ws.pop(web_addr)
            success_message = {
                "action": "REGISTER",
                "sender": "Server",
                "content": "Registration successful"
            }
            await web_socket.send(json.dumps(success_message))

            # --------------------------------------------DOTĄD DZIAŁA, PONIŻEJ ŚREDNIO--------------------------------------------

            # Przenieś rekord Operation do bazy User, zatwierdzając użytkownika
            user_data = {
                "username": operation_data["username"],
                "password": operation_data["password"],
                "mfa_id": operation_data["mfa_id"]
            }
            sqlite_cursor.execute("INSERT INTO User (username, password, mfa_id) VALUES (?, ?, ?)",
                                  (user_data["username"], user_data["password"], user_data["mfa_id"]))
            sqlite_conn.commit()

            # Usuń rekord z bazy Operation
            redis_conn.delete(operation_id)

        elif action == "LOGIN" and sender == "Mobile":
            operation_id = content.get("operation_id")
            mfa_id = content.get("mfa_id")

            # Sprawdź, czy ID operacji istnieje w bazie Operation
            if redis_conn.exists(operation_id):
                operation_data = json.loads(redis_conn.get(operation_id))

                # Odczytaj odpowiedni websocket
                web_addr = operation_data.get("web_addr")
                web_addr = operation_data.get("web_addr")
                web_socket = ws[web_addr]
                ws.pop(web_addr)

                # Sprawdź poprawność MFA ID w bazie User
                if operation_data.get("mfa_id") == mfa_id:
                    # Odpowiedz aplikacji webowej sukcesem
                    success_message = {
                        "action": "LOGIN",
                        "sender": "Server",
                        "content": "Login successful"
                    }
                    await web_socket.send(json.dumps(success_message))
                else:
                    # Odpowiedz aplikacji webowej błędem autoryzacji MFA
                    failure_message = {
                        "action": "LOGIN",
                        "sender": "Server",
                        "content": "MFA authentication failed"
                    }
                    await web_socket.send(json.dumps(failure_message))
            else:
                # Odpowiedz aplikacji mobilnej błędem braku operacji
                failure_message = {
                    "action": "LOGIN",
                    "sender": "Server",
                    "content": "Operation not found"
                }
                await websocket.send(json.dumps(failure_message))

start_server = websockets.serve(handle_client, "192.168.6.146", 30646)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

