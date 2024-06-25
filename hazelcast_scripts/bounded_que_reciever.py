import hazelcast

def main():
    client = hazelcast.HazelcastClient()
    queue = client.get_queue("bounded-queue").blocking()
    while True:
        item = queue.take()
        print(f"Received: {item}")


if __name__ == "__main__":
    main()
