from fastapi import FastAPI

app = FastAPI()


ffd = []

@app.get("/")
async def login():
    return {"mensaje":"chao"}

@app.get("/")
async def login():
    return {"mensaje":"jih"}

