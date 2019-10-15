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
                record = open('time.txt', 'w')
                record.write('Note that the module for constructing the DNS response message in part2.py is reused. \nThe time elapse starts when the proxy received the packet from client and ends when the proxy responded to client.\nTesting:\n')
                for i in range(5):
                    start_time = time.time()
                    response = construct_response_message(query, session=session)
                    s_receive.sendto(response, address)
                    time_elapsed = time.time() - start_time
                    record.write('DoH responded in {:.2f}s\n'.format(time_elapsed))
                    print('DoH responded in {:.2f}s'.format(time_elapsed))
                break


if __name__ == '__main__':
    dns_proxy_over_http_timing_test()
