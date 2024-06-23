from fastapi import FastAPI

app = FastAPI()

@app.get("/static_message/")
async def static_message():
    return "not implemented yet"