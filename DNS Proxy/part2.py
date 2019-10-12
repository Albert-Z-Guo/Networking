import socket
import requests

from dnslib import *

# IPv4 addresses with privileged port
CLIENT_ADDRESS = ('127.0.0.1', 53)

def dns_proxy_over_http():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_receive:
        s_receive.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = s_receive.recvfrom(4096)
            if query:
                # parse query
                message = DNSRecord.parse(query)
                question = message.questions[0]
                query_type = message.questions[0].qtype
                query_class = message.questions[0].qclass
                query_header = message.header

                # print('message:', message)
                # print('question:', message.questions)
                # print('QR:', query_header.qr)
                # print('AA:', query_header.aa)
                # print('TC:', query_header.tc)
                # print('RD:', query_header.rd)
                # print('RA:', query_header.ra)
                # print('AD:', query_header.ad)
                # print('CD:', query_header.cd)

                # https://developers.google.com/speed/public-dns/docs/doh/json
                # send query to Google DNS server
                parameters = {'name': str(question.qname), 'type': query_type}
                google_dns_response = requests.get('https://dns.google/resolve', params=parameters).json()
                print(google_dns_response)

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
                rdata = A(data)
                if query_type == 5:
                    rdata = CNAME(data)

                response = DNSRecord(query_header, q=question, a=RR(rname=name, rtype=query_type, rclass=query_class, ttl=TTL, rdata=rdata))

                # print('RA:', RA)
                # print('type:', query_type)
                # print('name:', name)
                # print('TTL:', TTL)
                # print('data:', data)
                # print('QR:', query_header.qr)
                # print('AA:', query_header.aa)
                # print('TC:', query_header.tc)
                # print('RD:', query_header.rd)
                # print('RA:', query_header.ra)
                # print('AD:', query_header.ad)
                # print('CD:', query_header.cd)
                # print(response)

                # send the response back to client
                s_receive.sendto(response.pack(), CLIENT_ADDRESS)
                print('response sent back to client:', s_receive.recv(4096))
                break

                # example response from part2.py
                # b'\xa5V\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x9b\x00\x04\xac\xd9\x05\x0e'
                # example response from part1.py
                # b'\xd4!\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\xbc\x00\x04\xac\xd9\x05\x0e'

if __name__ == '__main__':
    dns_proxy_over_http()
