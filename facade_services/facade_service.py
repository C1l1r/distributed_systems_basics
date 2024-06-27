import random

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import hazelcast
import uvicorn
import consul
import uuid

c = consul.Consul()

PORT_FROM=8090
PORT_TO=8200
def find_free_port(consul):
    services = consul.agent.services()
    ports = {s['Port'] for _, s in services.items()}
    for port in range(PORT_FROM, PORT_TO):
        if port not in ports:
            return port

app = FastAPI()
# Initialize the http client
http_client = httpx.AsyncClient()

port = find_free_port(c)
facade_config = {'name' : f'facede_service',
                 'service_id': str(uuid.uuid4()),
                 'address' : 'localhost',
                 'port': port
                 }
c.agent.service.register(**facade_config)
print(f"Registered facade-service {facade_config['service_id']}")

queue_name = c.kv.get('hazelcast_queue', index=None)[1]['Value'].decode()
print(f"Queue: {queue_name}")

hazelcast_port = int(random.choice(c.kv.get('hazelcast_ports')[1]['Value'].decode().split(',')))
print(f"Hazelcast port: {hazelcast_port}")

client = hazelcast.HazelcastClient(cluster_members = [f"127.0.0.1:{hazelcast_port}"])
message_queue = client.get_queue(queue_name)

# Define the Message model to send data
class Message(BaseModel):
    messageId: str
    message: str



@app.post("/message")
async def receive_message(request: Request):
    # Receive message from request body
    message = await request.body()
    message = message.decode("utf-8")  # Decode bytes to string
    # Generate a unique identifier
    uuid_str = str(uuid.uuid4())
    # Create message object
    msg = Message(messageId=uuid_str, message=message)

    ports = [values['Port'] for _, values in c.agent.services().items() if values['Service'] == 'logging_service']
    port = random.choice(ports)

    # Send the message to the logging service
    await http_client.post(f"http://localhost:{port}/save", json=msg.dict())
    message_queue.put(msg.dict())

    # Return confirmation response
    return {"message": "Received message with ID: " + uuid_str}

@app.get("/messages")
async def get_messages():
    # Fetch messages from the logging service

    ports = [values['Port'] for _, values in c.agent.services().items() if values['Service'] == 'logging_service']
    port = random.choice(ports)
    logging_service_messages = await http_client.get(f"http://localhost:{port}/messages")

    messagers_ports = [values['Port'] for _, values in c.agent.services().items() if values['Service'] == 'messages_service']
    messages_port = random.choice(messagers_ports)
    messages_services_messages = await http_client.get(f"http://localhost:{messages_port}/messages")


    return logging_service_messages.text + "\n ----------- \n" + messages_services_messages.text


    # Fetch response from the message service
    # message_service_response = await http_client.get("http://localhost:8082/static_message")
    # message_service_response = message_service_response.text

    # Combine and return the responses
    # return logging_service_messages + "\n" + message_service_response

@app.on_event("shutdown")
async def shutdown_event():
    # Properly close the client
    await http_client.aclose()

try:
    uvicorn.run(app, port=int(facade_config['port']))
except:
    c.service.deregister(facade_config['service_id'])