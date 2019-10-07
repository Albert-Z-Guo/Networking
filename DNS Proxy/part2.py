import struct

import socket
import requests

# IPv4 addresses with privileged port
DNS_SERVER_ADDRESS = ('8.8.8.8', 53) # Google public DNS servers
CLIENT_ADDRESS = ('127.0.0.1', 53)


def parse_udp(packet):
    header = packet[0:8]
    data = packet[8:]
    (source_port, dest_port, data_length, checksum) = struct.unpack("!HHHH", header)
    return source_port, dest_port, data_length, checksum, data

def dns_proxy_over_http():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = s_receive.recvfrom(4096)
            if query:
                print('query:', query)
                print('query address:', address)

                print(len(query))
                source_port, dest_port, data_length, checksum, data = parse_udp(query)
                print(source_port, dest_port, data_length, checksum, data)


                parameters = {
                    'name': 'baidu.com'
                }
                response = requests.get('https://dns.google/resolve', params=parameters)
                print(response.status_code)
                print(response.json())

                break


if __name__ == '__main__':
    dns_proxy_over_http()
