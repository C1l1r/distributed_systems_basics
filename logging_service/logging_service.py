import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hazelcast
import sys
import uvicorn

client = hazelcast.HazelcastClient(cluster_members = [f"127.0.0.1:{sys.argv[1]}"])
messages_map = client.get_map("messages")

app = FastAPI()



# Define the message model using Pydantic for data validation
class Message(BaseModel):
    messageId: str
    message: str


@app.post("/save")
async def save_message(message: Message):
    messages_map.put(message.messageId, message.message)
    print(f"Received and saved message: {message.message}")
    return {"status": "success"}

@app.get("/messages")
async def get_all_messages():
    print(messages_map.entry_set())
    return '\n'.join(f'{{messageId: "{mid}", message: "{ms}"}}' for mid, ms in messages_map.entry_set().result())

uvicorn.run(app, port=int(sys.argv[2]))