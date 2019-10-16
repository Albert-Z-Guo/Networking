import socket

import requests
from dnslib import *


# IPv4 addresses with privileged port
CLIENT_ADDRESS = ('127.0.0.1', 53)


def construct_response_message(query_message, session=None):
    # parse DNS query message
    message_query = DNSRecord.parse(query_message)
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
    if session:
        response = session.get('https://dns.google/resolve', params=parameters).json()
    else:
        response = requests.get('https://dns.google/resolve', params=parameters).json()
    # print(response)

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

    # note that only type A and type CNAME are tested
    if 'Answer' in response.keys():
        for answer in response['Answer']: # type A
            rdata = CNAME(answer['data']) if answer['type'] == 5 else A(answer['data']) # type = 1 means type A; type = 5 means type CNAME
            message_response.add_answer(RR(rname=answer['name'], rtype=answer['type'], rclass=query_class, ttl=answer['TTL'], rdata=rdata))
    # in case of authoritative answer in type SOA
    # e.g. nslookup -type=CNAME google.com 127.0.0.1
    if 'Authority' in response.keys():
        for authority in response['Authority']:
            data = authority['data'].split()
            times = [int(i) for i in data[2:]]
            message_response.add_auth(RR(rname=authority['name'], rtype=authority['type'], ttl=authority['TTL'], rdata=SOA(data[0], data[1], times)))

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
    # print('message_response:', message_response)

    return message_response.pack()

def dns_proxy_over_http():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_client:
        socket_client.bind(CLIENT_ADDRESS)
        while True: # keep listening
            query, address = socket_client.recvfrom(4096)
            if query:
                # send the response back to client
                response = construct_response_message(query)
                socket_client.sendto(response, address)


if __name__ == '__main__':
    dns_proxy_over_http()
