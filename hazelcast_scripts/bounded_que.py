import hazelcast
import time

def main():
    client = hazelcast.HazelcastClient()
    queue = client.get_queue("bounded-queue").blocking()
    for number in range(100):
        queue.put(number)
        print(f"Published: {number}")
        time.sleep(0.1)
    client.shutdown()

if __name__ == "__main__":
    main()