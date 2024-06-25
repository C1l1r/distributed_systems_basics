import hazelcast
import time

def main():
    client = hazelcast.HazelcastClient()
    topic = client.get_topic("my-topic").blocking()
    for number in range(1, 101):
        topic.publish(number)
        print(f"Published: {number}")
        time.sleep(0.1)
    client.shutdown()

if __name__ == "__main__":
    main()