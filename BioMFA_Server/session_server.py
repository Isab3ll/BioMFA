from fastapi import FastAPI
from pydantic import BaseModel
import redis
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

# Połączenie z Redis (baza danych Session)
redis_conn_session = redis.StrictRedis(host='localhost', port=6379, db=1)

# Klasa do przechowywania danych sesji
class Session(BaseModel):
    session_id: str
    username: str

@app.post("/is_logged")
async def is_logged(session: Session):
    # Sprawdź istnienie sesji
    session_data = redis_conn_session.get(session.session_id)
    if session_data is not None:
        return {"is_logged": True}
    return {"is_logged": False}

@app.post("/logout")
async def logout(session: Session):
    # Usuń sesję z bazy danych Session
    redis_conn_session.delete(session.session_id)
    return {"status": "OK"}
