from fastapi import FastAPI
import sys
import hazelcast
import sys
import uvicorn
import threading

app = FastAPI()
client = hazelcast.HazelcastClient(cluster_members = [f"127.0.0.1:{sys.argv[1]}"])
queue = client.get_queue("bounded-queue").blocking()

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
    uvicorn.run(app, port=int(sys.argv[2]))

thread = threading.Thread(target=start_uvicorn)
thread.daemon = True

thread.start()
start_queue()
