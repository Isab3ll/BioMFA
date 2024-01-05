from fastapi import FastAPI
import json
from pydantic import BaseModel
import redis

app = FastAPI()

# Połączenie z Redis (baza danych Session)
redis_conn_session = redis.StrictRedis(host='localhost', port=6379, db=1)

# Klasa do przechowywania danych sesji
class Session(BaseModel):
    session_id: str
    username: str

@app.post("/is_logged")
async def is_logged(session: Session):
    # Sprawdź czy sesja istnieje w bazie sesji
    session_data = redis_conn_session.get(session.session_id)
    if session_data is not None:
        # Sprawdź czy nazwa użytkownika w sesji jest zgodna z nazwą w parametrze
        session_data = json.loads(session_data)
        username = session_data["username"]
        if username == session.username:
            return {"is_logged": True}
    return {"is_logged": False}

@app.post("/logout")
async def logout(session: Session):
    # Usuń sesję z bazy danych Session
    redis_conn_session.delete(session.session_id)
    return {"status": "OK"}
