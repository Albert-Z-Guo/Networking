from collections import defaultdict
import os
import select
import socket
import struct
import sys
import time


ICMP_ECHO_REQUEST = 8
ID_RTTs_dict = defaultdict(list)


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


def receive_one_ping(mySocket, ID, timeout, destAddr):
    while 1:
        what_ready = select.select([mySocket], [], [], timeout)
        if what_ready[0] == []:  # Timeout
            return 'Request timed out.'
        recPacket, addr = mySocket.recvfrom(1024)

        # read the packet and parse the source IP address, you will need this part for traceroute
        ip_version = int(bin(struct.unpack('B', recPacket[0:1])[0])[2:].zfill(8)[:4], 2)
        print('IP version: {}'.format(ip_version))
        
        # calculate and return the round trip time for this ping
        if ip_version == 4:
            print('TTL: {}'.format(struct.unpack('B', recPacket[8:9])[0]))
            RTT = time.time() - struct.unpack('d', recPacket[28:36])[0]
            # if ID == icmp_id: ID_RTTs_dict[ID].append(RTT)
            ID_RTTs_dict[ID].append(RTT)
            source_address = recPacket[12:16]
            icmp_header = recPacket[20:28]
            
        elif ip_version == 6:
            source_address = recPacket[8:24]
            icmp_header = recPacket[40:48]
        
        print('Source Address: {}'.format(source_address))

        # handle different response type and error code, display error message to the user
        icmp_type, icmp_code, icmp_chechsum, icmp_id, icmp_seq = struct.unpack('BBHHH', icmp_header)
        print('ICMP Chechsum: {}'.format(icmp_chechsum))
        print('ICMP ID:       {}'.format(icmp_id))
        print('ICMP Sequence: {}'.format(icmp_seq))

        if icmp_type == 0:
            print('ICMP Type 0: Echo Reply')
        elif icmp_type == 3:
            print('ICMP Type 3: Destination Unreachable\nDescription:')
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
        else:
            print('ICMP Type {}'.format(icmp_type))
            print('ICMP Code {}'.format(icmp_code))
        
        # tests
        ip_header = recPacket[:20]
        print('header checksum: {}'.format(struct.unpack('@H', ip_header[10:12])[0]))
        print('actual header checksum: {}'.format(checksum(ip_header[:10])))
        print('')
        
        if ip_version == 6: return 'hop_limit: ' + str(struct.unpack('B', recPacket[7:8])[0])
        return 'RTT: {:.5f}s'.format(RTT)


def send_one_ping(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum

    # struct -- Interpret strings as packed binary data
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack('d', time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(str(header + data))
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    # AF_INET address must be tuple, not str # Both LISTS and TUPLES consist of a number of objects
    mySocket.sendto(packet, (destAddr, 1))
    # which can be referenced by their position number within the object.


def do_one_ping(destAddr, timeout):
    icmp = socket.getprotobyname('icmp')
    # SOCK_RAW is a powerful socket type. For more details: http://sock-raw.org/papers/sock_raw
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    # Return the current process i
    myID = os.getpid() & 0xFFFF
    send_one_ping(mySocket, destAddr, myID)
    delay = receive_one_ping(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = socket.gethostbyname(host)
    print('Pinging ' + dest + ' using Python:')
    print('')
    # Send ping requests to a server separated by approximately one second
    while 1:
        delay = do_one_ping(dest, timeout)
        print(delay)
        time.sleep(1)  # one second
    return delay


if __name__ == '__main__':
    try:
        ping(sys.argv[1])
    except KeyboardInterrupt:
        print('\n--- Round-trip Time  (RTT) statistics ---')
        RTTs = ID_RTTs_dict[os.getpid() & 0xFFFF]
        print('min RTT : {:5f}s'.format(min(RTTs)))
        print('max RTT : {:5f}s'.format(max(RTTs)))
        print('mean RTT: {:5f}s'.format(sum(RTTs)/len(RTTs)))
