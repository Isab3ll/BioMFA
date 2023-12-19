from fastapi import FastAPI

app = FastAPI()

@app.post("/is_logged")
async def is_logged():
    return {"is_logged": True}
