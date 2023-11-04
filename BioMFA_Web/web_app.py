import asyncio
import websockets
import json

# Zmienna do przechowywania informacji o zarejestrowanych użytkownikach
registered_users = {}

# Zmienna do przechowywania informacji o użytkownikach zalogowanych do MFA
logged_in_users = {}

# Adres serwera WebSocket
server_address = "ws://frog01.mikr.us:30646"

async def main():
    async with websockets.connect(server_address) as websocket:
        while True:
            print("1. Register")
            print("2. Login")
            choice = input("Choose an action (1/2): ")

            if choice == "1":
                username = input("Enter username: ")
                password = input("Enter password: ")
                message = {"action": "REGISTER", "content": {"username": username, "password": password}}
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                print(response)
                operation_id = json.loads(response).get("content").get("operation_id")
                result = await websocket.recv()
                print(result)

            elif choice == "2":
                username = input("Enter username: ")
                password = input("Enter password: ")
                message = {"action": "LOGIN", "content": {"username": username, "password": password}}
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                print(response)
                content = json.loads(response).get("content")
                if content != "Invalid credentials":
                    operation_id = content.get("operation_id")
                    result = await websocket.recv()
                    print(result)            

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
