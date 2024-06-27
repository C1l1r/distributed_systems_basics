import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hazelcast
import uvicorn
import httpx
import uuid
import consul
import random

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

c = consul.Consul()
port = find_free_port(c)
logging_config = {'name' : f'logging_service',
                 'service_id': str(uuid.uuid4()),
                 'address' : 'localhost',
                 'port': port
                 }
c.agent.service.register(**logging_config)
print(f"Registered logging-service {logging_config['service_id']}")


hazelcast_port = int(random.choice(c.kv.get('hazelcast_ports')[1]['Value'].decode().split(',')))
print(f"Hazelcast port: {hazelcast_port}")

client = hazelcast.HazelcastClient(cluster_members = [f"127.0.0.1:{hazelcast_port}"])

message_name = c.kv.get('hazelcast_message', index=None)[1]['Value'].decode()
print(f"Messages: {message_name}")
messages_map = client.get_map(message_name)

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

uvicorn.run(app, port=logging_config['port'])