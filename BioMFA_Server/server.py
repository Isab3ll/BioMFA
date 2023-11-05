import asyncio
import hashlib
import json
import random
import redis
import sqlite3
import uuid
import websockets

# Połączenie z SQLite (baza danych User)
sqlite_conn = sqlite3.connect('users.db')
sqlite_cursor = sqlite_conn.cursor()
sql = "CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, salt TEXT, mfa_id TEXT)"
sqlite_cursor.execute(sql)

# Połączenie z Redis (baza danych Operation)
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

# Spis otwartych websocketów
ws = {}

# Funkcja do generowania soli
def generate_salt():
    return uuid.uuid4().hex

# Funkcja do hashowania hasła z solą
def hash_password(password, salt):
    return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()

# Funkcja do porównywania haseł
def compare_passwords(password, salt, hashed_password):
    return hash_password(password, salt) == hashed_password

# Funkcja generująca unikalne ID operacji
def generate_operation_id():
    return str(random.randint(100000, 999999))

# Funkcja obsługująca rejestrację użytkownika
async def register_user(username, password, websocket):
    # Wygeneruj ID operacji i sól
    operation_id = generate_operation_id()
    salt = generate_salt()

    # Zapisz websocket i ID operacji w bazie Operation
    ws[websocket.remote_address[0]] = websocket
    operation_data = {
        "operation": "REGISTER",
        "username": username,
        "password": hash_password(password, salt),
        "salt": salt,
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
    sqlite_cursor.execute("SELECT username, password, salt FROM User WHERE username=?", (username,))
    user_data = sqlite_cursor.fetchone()
    valid_user = user_data is not None
    valid_credentials = compare_passwords(password, user_data[2], user_data[1]) if valid_user else False

    if not(valid_credentials):
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

# Funkcja obsługująca autoryzację MFA
async def mfa_authenticate(operation_id, mfa_id):
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
            "salt": operation_data["salt"],
            "mfa_id": operation_data["mfa_id"]
        }
        sqlite_cursor.execute("INSERT INTO User (username, password, salt, mfa_id) VALUES (?, ?, ?, ?)",
                            (user_data["username"], user_data["password"], user_data["salt"], user_data["mfa_id"]))
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
            await mfa_authenticate(operation_id, mfa_id)

start_server = websockets.serve(handle_client, "192.168.6.146", 30646)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    pass
