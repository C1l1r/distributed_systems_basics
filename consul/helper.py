PORT_FROM=8090
PORT_TO=8200
def find_free_port(consul):
    services = consul.agent.services()
    ports = {s['Port'] for _, s in services.items()}
    for port in range(PORT_FROM, PORT_TO):
        if port not in ports:
            return port