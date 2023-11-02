import asyncio
import websockets
import json

# Zmienna do przechowywania informacji o zarejestrowanych użytkownikach
registered_users = {}

# Zmienna do przechowywania informacji o użytkownikach zalogowanych do MFA
logged_in_users = {}

# Adres serwera WebSocket
server_address = "ws://frog01.mikr.us:30646"

# Funkcja do obsługi rejestracji
async def register(username, password, websocket):
    if username in registered_users:
        return {"action": "REGISTER", "content": "Username already exists."}
    registered_users[username] = password
    return {"action": "REGISTER", "content": "Registration successful."}

# Funkcja do obsługi logowania
async def login(username, password, websocket):
    if username not in registered_users or registered_users[username] != password:
        return {"action": "LOGIN", "content": "Invalid credentials."}
    # Logowanie udane, generowanie MFA ID (to tylko przykład)
    mfa_id = username + "_mfa"
    logged_in_users[username] = mfa_id
    return {"action": "LOGIN", "content": mfa_id}

async def main():
    async with websockets.connect(server_address) as websocket:
        while True:
            print("1. Register")
            print("2. Login")
            choice = input("Choose an action (1/2): ")

            if choice == "1":
                username = input("Enter username: ")
                password = input("Enter password: ")
                message = {"action": "REGISTER", "sender": "Web", "content": {"username": username, "password": password}}
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                print(response)
                success = await websocket.recv()
                print(success)

            elif choice == "2":
                username = input("Enter username: ")
                password = input("Enter password: ")
                message = {"action": "LOGIN", "sender": "Web", "content": {"username": username, "password": password}}
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                response_data = json.loads(response)
                if response_data.get("action") == "LOGIN" and not response_data.get("content").startswith("Invalid"):
                    mfa_id = response_data.get("content")
                    print(f"Logged in. Your MFA ID: {mfa_id}")
                    # Tutaj możesz wykonywać operacje związane z zalogowanym użytkownikiem

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
