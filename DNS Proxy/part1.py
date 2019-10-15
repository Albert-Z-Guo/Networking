import socket


# IPv4 addresses with privileged port
DNS_SERVER_ADDRESS = ('8.8.8.8', 53)  # Google public DNS servers
CLIENT_ADDRESS = ('127.0.0.1', 53)


def dns_proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_client:
        socket_client.bind(CLIENT_ADDRESS)
        while True: # keep receiving
            query, address = socket_client.recvfrom(4096)
            if query:
                print('\nquery:', query)
                print('query address:', address)

                # forward query to Google DNS server
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_server:
                    socket_server.sendto(query, DNS_SERVER_ADDRESS)
                    response, response_address = socket_server.recvfrom(4096)
                    if response:
                        print('response:', response)
                        print('response address:', response_address)
                        socket_client.sendto(response, address)


if __name__ == '__main__':
    dns_proxy()
