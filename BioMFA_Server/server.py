import asyncio
import json
import random
import redis
import sqlite3
import websockets

# Połączenie z SQLite (baza danych User)
sqlite_conn = sqlite3.connect('users.db')
sqlite_cursor = sqlite_conn.cursor()
sql = "CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, mfa_id TEXT)"
sqlite_cursor.execute(sql)

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
        "operation": "REGISTER",
        "username": username,
        "password": password,
        "web_addr": websocket.remote_address[0]
    }
    redis_conn.set(operation_id, json.dumps(operation_data))

    # Odpowiedz z ID operacji
    response = {
        "action": "REGISTER",
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
            "content": "Invalid credentials"
        }
        await websocket.send(json.dumps(response))
    else:
        # Logowanie udane, wygeneruj ID operacji
        operation_id = generate_operation_id()
        # Zapisz websocket i ID operacji w bazie Operation
        ws[websocket.remote_address[0]] = websocket
        operation_data = {
            "operation": "LOGIN",
            "username": username,
            "web_addr": websocket.remote_address[0]
        }
        redis_conn.set(operation_id, json.dumps(operation_data))

        # Odpowiedz z ID operacji
        response = {
            "action": "LOGIN",
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
        content = message_data.get("content")

        if action == "REGISTER":
            username = content.get("username")
            password = content.get("password")
            await register_user(username, password, websocket)

        elif action == "LOGIN":
            username = content.get("username")
            password = content.get("password")
            await login_user(username, password, websocket)

        elif action == "RESET":
            operation_id = content.get("operation_id")
            if redis_conn.exists(operation_id):
                redis_conn.delete(operation_id)

        elif action == "MFA":
            operation_id = content.get("operation_id")
            mfa_id = content.get("mfa_id")

            #  Odczytaj typ operacji z bazy Operation
            operation_data = json.loads(redis_conn.get(operation_id))
            operation = operation_data.get("operation")

            # Odczytaj odpowiedni websocket
            web_addr = operation_data.get("web_addr")
            web_socket = ws[web_addr]
            ws.pop(web_addr)

            if operation == "REGISTER":
                # Dopisz mfa_id do odpowiedniego rekordu w bazie Operation
                operation_data["mfa_id"] = mfa_id
                redis_conn.set(operation_id, json.dumps(operation_data))

                # Prześlij komunikat sukcesu
                success_message = {
                    "action": "REGISTER",
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
                redis_conn.delete(operation_id)

            elif operation == "LOGIN":
                # Sprawdź poprawność MFA ID w bazie User
                sqlite_cursor.execute("SELECT mfa_id FROM User WHERE username=?", (operation_data["username"],))
                mfa_db = sqlite_cursor.fetchone()[0]
                redis_conn.delete(operation_id)
                if mfa_db == mfa_id:
                    # Odpowiedz aplikacji webowej sukcesem
                    success_message = {
                        "action": "LOGIN",
                        "content": "Login successful"
                    }
                    await web_socket.send(json.dumps(success_message))
                else:
                    # Odpowiedz aplikacji webowej błędem autoryzacji MFA
                    failure_message = {
                        "action": "LOGIN",
                        "content": "MFA authentication failed"
                    }
                    await web_socket.send(json.dumps(failure_message))

start_server = websockets.serve(handle_client, "192.168.6.146", 30646)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    pass
