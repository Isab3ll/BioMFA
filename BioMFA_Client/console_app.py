import asyncio
import hashlib
import websockets
import json

server_address = "wss://biomfa.online/ws"
global_websocket = None
operation_id = None

# Funkcja do hashowania hasła
def hash_password(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()

# Funkcja do resetowania operacji
def reset_operation():
    if operation_id is not None:
        try:
            message = {"action": "RESET", "content": {"operation_id": operation_id}}
            asyncio.get_event_loop().run_until_complete(global_websocket.send(json.dumps(message)))
        except websockets.exceptions.ConnectionClosedOK:
            pass

async def main():
    global global_websocket, operation_id
    async with websockets.connect(server_address) as websocket:
        global_websocket = websocket
        try:
            while True:
                print("1. Register")
                print("2. Login")
                choice = input("Choose an action (1/2): ")
                # Operacja rejestracji
                if choice == "1":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    hashed_password = hash_password(password)
                    message = {"action": "REGISTER", "content": {"username": username, "password": hashed_password}}
                    await websocket.send(json.dumps(message))
                    response = await websocket.recv()
                    print(response)
                    content = json.loads(response).get("content")
                    if content == "Username already exists":
                        continue
                    operation_id = json.loads(response).get("content").get("operation_id")
                    try:
                        result = await asyncio.wait_for(websocket.recv(), timeout=60)
                        print(result)
                    except asyncio.TimeoutError:
                        reset_operation()
                # Operacja logowania
                elif choice == "2":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    hashed_password = hash_password(password)
                    message = {"action": "LOGIN", "content": {"username": username, "password": hashed_password}}
                    await websocket.send(json.dumps(message))
                    response = await websocket.recv()
                    print(response)
                    content = json.loads(response).get("content")
                    if content != "Invalid credentials":
                        operation_id = content.get("operation_id")
                        try:
                            result = await asyncio.wait_for(websocket.recv(), timeout=60)
                            print(result)
                        except asyncio.TimeoutError:
                            reset_operation()
        except websockets.exceptions.ConnectionClosedOK:
            pass   

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        reset_operation()
        asyncio.get_event_loop().run_until_complete(global_websocket.close())
