import time
import socket

import requests
from dnslib import *
from part2 import construct_response_message


# IPv4 addresses with privileged port
CLIENT_ADDRESS = ('127.0.0.1', 53)

def dns_proxy_over_http_timing_test():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = s_receive.recvfrom(4096)
            session = requests.Session()
            if query:
                for i in range(10):
                    start_time = time.time()
                    response = construct_response_message(query, session=session)
                    s_receive.sendto(response, address)
                    print('DoH responded in {:.2f}s'.format(time.time() - start_time))


if __name__ == '__main__':
    dns_proxy_over_http_timing_test()
