from fastapi import FastAPI
import sys
import hazelcast
import uvicorn
import threading
import httpx
import random
import uuid
import consul

PORT_FROM=8090
PORT_TO=8200
def find_free_port(consul):
    services = consul.agent.services()
    ports = {s['Port'] for _, s in services.items()}
    for port in range(PORT_FROM, PORT_TO):
        if port not in ports:
            return port

app = FastAPI()

http_sync = httpx.Client()

c = consul.Consul()

port = find_free_port(c)
messages_config = {'name' : f'messages_service',
                 'service_id': str(uuid.uuid4()),
                 'address' : 'localhost',
                 'port': port
                 }
c.agent.service.register(**messages_config)
print(f"Registered messages-service {messages_config['service_id']}")


hazelcast_port = int(random.choice(c.kv.get('hazelcast_ports')[1]['Value'].decode().split(',')))
print(f"Hazelcast port: {hazelcast_port}")
client = hazelcast.HazelcastClient(cluster_members = [f"127.0.0.1:{hazelcast_port}"])

queue_name = c.kv.get('hazelcast_queue', index=None)[1]['Value'].decode()
print(f"Queue: {queue_name}")
queue = client.get_queue(queue_name).blocking()


messages = []
@app.get("/messages")
async def single_service_messages():
    print('\n'.join(f'{{messageId: "{m["messageId"]}", message: "{m["message"]}"}}' for m in messages))
    return '\n'.join(f'{{messageId: "{m["messageId"]}", message: "{m["message"]}"}}' for m in messages)

def start_queue():
    while True:
        item = queue.take()
        messages.append(item)
        print( f"Received: {item}")

def start_uvicorn():
    uvicorn.run(app, port=messages_config['port'])

thread = threading.Thread(target=start_uvicorn)
thread.daemon = True

thread.start()
start_queue()
