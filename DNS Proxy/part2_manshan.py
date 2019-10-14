import socket
from dnslib import *
import requests

def get_res(name):
    response = requests.get('https://dns.google/resolve', params={
        'name': name
    })
    json_response = response.json()
    print(json_response)
    return json_response['Answer']

def create_answer(udp,json_response):
    d=DNSRecord(udp.header,q=udp.q)
    udp.header.set_qr(1)
    for i in json_response:
        if i['type']==1:
            temp=RR(i['name'],rdata=A(i['data']),rtype=1)
            d.add_answer(temp)
        elif i['type']==5:
            temp=RR(i['name'],rdata=CNAME(i['data']),rtype=5)
            d.add_answer(temp)
        else:
            continue
    return d.pack()


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server_address = ('127.0.0.1', 53)
        sock.bind(server_address)
        while True:
            data, address = sock.recvfrom(4096)
            udp = DNSRecord.parse(data)
            name=udp.get_q().qname.__str__()
            resp=get_res(name)
            if data:
                answer=create_answer(udp,resp)
                sock.sendto(answer,address)

server()
