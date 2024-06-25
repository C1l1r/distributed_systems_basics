import hazelcast

def main():
    # Configure and initialize the Hazelcast client
    client = hazelcast.HazelcastClient()

    # Access the distributed map on the cluster. If it doesn't exist, it will be created.
    my_map = client.get_map("my-distributed-map").blocking()

    map_variable = {f"key{i}": f"value{i}" for i in range(1000)}
    my_map.put_all(map_variable)

    client.shutdown()

if __name__ == "__main__":
    main()