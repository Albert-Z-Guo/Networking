import socket


# IPv4 addresses with privileged port
DNS_SERVER_ADDRESS = ('8.8.8.8', 53) # Google public DNS servers
CLIENT_ADDRESS = ('127.0.0.1', 53)


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True:
            query, address = s_receive.recvfrom(4096)
            if query:
                print('query:', query)
                print('query address:', address)

                # send data to Google's DNS server
                print('\nforwarding query to Google DNS server...')
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_forward:
                    s_forward.sendto(query, DNS_SERVER_ADDRESS)
                    response, response_address = s_forward.recvfrom(4096)
                    if response:
                        print('response:', response)
                        print('response address:', response_address)
                        print(response.decode(encoding="utf-8", errors='ignore'))
                break


if __name__ == '__main__':
    server()
