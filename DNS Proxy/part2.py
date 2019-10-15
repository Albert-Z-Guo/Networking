import socket

import requests
from dnslib import *

# IPv4 addresses with privileged port
CLIENT_ADDRESS = ('127.0.0.1', 53)

def dns_proxy_over_http():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_client:
        socket_client.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = socket_client.recvfrom(4096)
            if query:
                # parse DNS query message
                message_query = DNSRecord.parse(query)
                question = message_query.questions[0].qname
                query_type = message_query.questions[0].qtype
                query_class = message_query.questions[0].qclass # Class field is 1 for Internet data.
                query_header = message_query.header

                # print('query')
                # print('question:', question)
                # print('type:', query_type)
                # print('class:', query_class)
                # print('QR:', query_header.qr)
                # print('AA:', query_header.aa)
                # print('TC:', query_header.tc)
                # print('RD:', query_header.rd)
                # print('RA:', query_header.ra)
                # print('AD:', query_header.ad)
                # print('CD:', query_header.cd)

                # https://developers.google.com/speed/public-dns/docs/doh/json
                # send query to Google DNS server
                parameters = {'name': str(question), 'type': query_type}
                response = requests.get('https://dns.google/resolve', params=parameters).json()
                print(response)

                # construct DNS response message
                query_header.set_qr(1) # set QR = 1 for response
                query_header.set_tc(response['TC'])
                query_header.set_rd(response['RD']) # always true for Google Public DNS
                query_header.set_ra(response['RA'] ) # always true for Google Public DNS
                query_header.set_ad(response['AD'])
                query_header.set_cd(response['CD'])

                message_response = DNSRecord(query_header)

                # in case of multiple questions and answers
                for question in response['Question']:
                    message_response.add_question(DNSQuestion(qname=question['name'], qtype=question['type']))
                for answer in response['Answer']:
                    rdata = CNAME(answer['data']) if answer['type'] == 5 else A(answer['data']) # type = 1 means type A; type = 5 means type CNAME
                    message_response.add_answer(RR(rname=answer['name'], rtype=answer['type'], rclass=query_class, ttl=answer['TTL'], rdata=rdata))

                # print('response:')
                # print('name:', message_response.a.rname)
                # print('type:', message_response.a.rtype)
                # print('TTL:', message_response.a.ttl) #  TTL field is the number of seconds for which the RR can be cached.
                # print('data:', message_response.a.rdata)
                # print('QR:', query_header.qr) # Query (0) Response (1)
                # print('AA:', query_header.aa) # Authoritative Answer
                # print('TC:', query_header.tc) # Truncated Answer
                # print('RD:', query_header.rd) # Recursion Desired
                # print('RA:', query_header.ra) # Recursion Available
                # print('AD:', query_header.ad) # Authentic Data
                # print('CD:', query_header.cd) # Checking Disabled

                # send the response back to client
                socket_client.sendto(message_response.pack(), address)
                print('response sent back to client:', message_response.pack())

                # example response from part1.py
                # b'\xd3\x0b\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\xe3\x00\x04\xd8:\xc0\xee'

                # example response from part2.py
                # b'\x8f\xc5\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01 \x00\x04\xd8:\xc0\xee'


if __name__ == '__main__':
    dns_proxy_over_http()
