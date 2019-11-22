from __future__ import print_function
import os
import select
import socket
import struct
import sys
import time


ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(string[count+1]) * 256 + ord(string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def build_packet():
    ID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(str(header + data))
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    return packet


def get_route(hostname):
    for ttl in range(1, MAX_HOPS):
        print('TTL: {}'.format(ttl))
        for tries in range(TRIES):
            print('\tTry: {}'.format(tries))
            # create ICMP socket, connect to destination IP, set timeout and time-to-live
            icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
            icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            try:
                # create ICMP ping packet, record the time delay of getting response detect timeout
                icmp_socket.sendto(build_packet(), (socket.gethostbyname(hostname), 1))
                start_time = time.time()
                what_ready = select.select([icmp_socket], [], [], TIMEOUT)
                if what_ready[0] == []: return 'Request timed out.'
                recPacket, addr = icmp_socket.recvfrom(1024)
                print('\tRTT: {:.3f} ms'.format((time.time() - start_time)*1000))
                print('\tRouter IP Address: {} '.format(addr[0]))
                try:
                    print('\tRouter Name: {}'.format(socket.gethostbyaddr(addr[0])[0]))
                except:
                    print('\tRouter name is not available.')
            except Exception as e:
                print('\t{}'.format(e))
                continue
            else:
                # parse and handle different response types
                icmp_type, icmp_code, icmp_chechsum, icmp_id, icmp_seq = struct.unpack('BBHHH', recPacket[20:28])
                if icmp_type == 0:
                    print('\tICMP Type 0: Echo Reply')
                elif icmp_type == 3:
                    print('\tICMP Type 3: Destination Unreachable\n\tICMP Code {}:'.format(icmp_code), end=' ')
                    if icmp_code == 0: print('Net Unreachable')
                    if icmp_code == 1: print('Host Unreachable')
                    if icmp_code == 2: print('Protocol Unreachable')
                    if icmp_code == 3: print('Port Unreachable')
                    if icmp_code == 4: print("Fragmentation Needed and Don't Fragment was Set")
                    if icmp_code == 5: print('Source Route Failed')
                    if icmp_code == 6: print('Destination Network Unknown')
                    if icmp_code == 7: print('Destination Host Unknown')
                    if icmp_code == 8: print('Source Host Isolated')
                    if icmp_code == 9: print('Communication with Destination Network is Administratively Prohibited')
                    if icmp_code == 10: print('Communication with Destination Host is Administratively Prohibited')
                    if icmp_code == 11: print('Destination Network Unreachable for Type of Service')
                    if icmp_code == 12: print('Destination Host Unreachable for Type of Service')
                    if icmp_code == 13: print('Communication Administratively Prohibited')
                    if icmp_code == 14: print('Host Precedence Violation')
                    if icmp_code == 15: print('Precedence cutoff in effect')
                elif icmp_type == 11:
                    print('\tICMP Type 11: Time Exceeded\n\tICMP Code {}:'.format(icmp_code), end=' ')
                    if icmp_code == 0: print('Time to Live exceeded in Transit')
                    if icmp_code == 1: print('Fragment Reassembly Time Exceeded')
                else:
                    print('\tICMP Type {}'.format(icmp_type))
                    print('\tICMP Code {}'.format(icmp_code))
                print('')
            finally:
                icmp_socket.close()


if __name__ == "__main__":
    try:
        get_route(sys.argv[1])
    except IndexError:
        print('A hostname argument is required. e.g. $sudo python traceroute.py google.com')
