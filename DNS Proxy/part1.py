import socket


# IPv4 addresses with privileged port
DNS_SERVER_ADDRESS = ('8.8.8.8', 53) # Google public DNS servers
CLIENT_ADDRESS = ('127.0.0.1', 53)


def dns_proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = s_receive.recvfrom(4096)
            if query:
                print('query:', query)
                print('query address:', address)
                print('\nforwarding query to Google DNS server...')

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_forward:
                    while True: # keep sending queries until receiving a response
                        s_forward.sendto(query, DNS_SERVER_ADDRESS)
                        response, response_address = s_forward.recvfrom(4096)
                        if response:
                            print('response:', response)
                            print('response address:', response_address)

                            s_forward.sendto(response, CLIENT_ADDRESS)
                            print('response send back to client:', s_receive.recv(4096))
                            break
                break


if __name__ == '__main__':
    dns_proxy()
