import sys
import socket
import dns.resolver

def server():
    # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            res=''
        # Bind the socket to the port
            server_address = ('127.0.0.1', 53)
            sock.bind(server_address)
            while True:
                data, address = sock.recvfrom(4096)
                if data:
                    sock1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    DNS_server=('8.8.8.8',53)
                    sock1.sendto(data,DNS_server)
                    res, server = sock1.recvfrom(4096)
                    sock.sendto(res,address)
              
server()





