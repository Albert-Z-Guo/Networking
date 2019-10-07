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

def extract_string(bytes):
    message = []
    for i in bytes:
        if i >= 3:
            if i < 10:
                message.append('.')
            else:
                message.append(chr(i))
    return ''.join(message[1:])

def dns_proxy_over_http():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = s_receive.recvfrom(4096)
            if query:
                print('query:           ', query)
                print('query address:   ', address)

                source_port, dest_port, data_length, checksum, data = parse_udp(query)
                print('source port:     ', source_port)
                print('destination port:', dest_port)
                print('data length:     ', data_length)
                print('checksum:        ', checksum)

                print('data:            ', data)
                print('data decoded:    ', extract_string(data))

                parameters = {'name': extract_string(data)}
                response = requests.get('https://dns.google/resolve', params=parameters)
                print(response.json())

                break


if __name__ == '__main__':
    dns_proxy_over_http()
