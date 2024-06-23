from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Define the message model using Pydantic for data validation
class Message(BaseModel):
    messageId: str
    message: str

# Dictionary to store messages
messages = {}

@app.post("/save")
async def save_message(message: Message):
    # Save the message into the dictionary using UUID as the key
    messages[message.messageId] = message.message
    print(f"Received and saved message: {message.message}")
    return {"status": "success"}

@app.get("/messages")
async def get_all_messages():
    # Concatenate all messages into a single string separated by new lines
    return "\n".join(messages.values())
