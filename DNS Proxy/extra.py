import time
import socket
import requests

from dnslib import *


# IPv4 addresses with privileged port
CLIENT_ADDRESS = ('127.0.0.1', 53)

def dns_proxy_over_http_timing_test():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = s_receive.recvfrom(4096)
            session = requests.Session()
            if query:
                for i in range(6):
                    start_time = time.time()
                    # parse query
                    message = DNSRecord.parse(query)
                    question = message.questions[0]
                    query_type = message.questions[0].qtype
                    query_class = message.questions[0].qclass
                    query_header = message.header

                    # send query to Google DNS server
                    parameters = {'name': str(question.qname), 'type': query_type}
                    google_dns_response = session.get('https://dns.google/resolve', params=parameters).json()

                    # parse response from Google DNS server
                    TC = google_dns_response['TC']
                    RD = google_dns_response['RD']
                    RA = google_dns_response['RA']
                    AD = google_dns_response['AD']
                    CD = google_dns_response['CD']
                    query_type = google_dns_response['Question'][0]['type'] # type 1 means type A
                    name = google_dns_response['Answer'][0]['name']
                    TTL = google_dns_response['Answer'][0]['TTL']
                    data = google_dns_response['Answer'][0]['data']

                    # construct response
                    query_header.set_qr(1) # set QR = 1 for response
                    query_header.set_tc(TC)
                    query_header.set_rd(RD)
                    query_header.set_ra(RA)
                    query_header.set_ad(AD)
                    query_header.set_cd(CD)
                    response = DNSRecord(query_header, q=question, a=RR(rname=name, rtype=query_type, rclass=query_class, ttl=TTL, rdata=A(data)))

                    # send the response back to client
                    s_receive.sendto(response.pack(), CLIENT_ADDRESS)
                    print('response sent back to client:', s_receive.recv(4096))
                    print('DoH responded in {:.2f}s'.format(time.time() - start_time))
            break

if __name__ == '__main__':
    dns_proxy_over_http_timing_test()
