import hazelcast

def message_listener(message):
    print(f"Received: {message.message}")

def main():
    client = hazelcast.HazelcastClient()
    topic = client.get_topic("my-topic").blocking()
    topic.add_listener(message_listener)
    input("Press enter to stop the subscriber...\n")
    client.shutdown()

if __name__ == "__main__":
    main()
