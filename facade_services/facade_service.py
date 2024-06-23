from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import uuid

app = FastAPI()

# Define the Message model to send data
class Message(BaseModel):
    messageId: str
    message: str

# Initialize the http client
http_client = httpx.AsyncClient()

@app.post("/message")
async def receive_message(request: Request):
    # Receive message from request body
    message = await request.body()
    message = message.decode("utf-8")  # Decode bytes to string

    # Generate a unique identifier
    uuid_str = str(uuid.uuid4())

    # Create message object
    msg = Message(messageId=uuid_str, message=message)

    # Send the message to the logging service
    await http_client.post("http://localhost:8081/save", json=msg.dict())

    # Return confirmation response
    return {"message": "Received message with ID: " + uuid_str}

@app.get("/messages")
async def get_messages():
    # Fetch messages from the logging service
    logging_service_messages = await http_client.get("http://localhost:8081/messages")
    logging_service_messages = logging_service_messages.text

    # Fetch response from the message service
    message_service_response = await http_client.get("http://localhost:8082/static_message")
    message_service_response = message_service_response.text

    # Combine and return the responses
    return logging_service_messages + "\n" + message_service_response

@app.on_event("shutdown")
async def shutdown_event():
    # Properly close the client
    await http_client.aclose()
