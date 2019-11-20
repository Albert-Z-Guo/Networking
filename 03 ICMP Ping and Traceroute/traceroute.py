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
# The packet that we shall send to each router along the path is the ICMP echo # request packet, which is exactly what we had used in the ICMP ping exercise. # We shall use the same packet that we built in the Ping exercise


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
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.
    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
    # So the function ending should look like this
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
    icmp = socket.getprotobyname("icmp")
    timeLeft = TIMEOUT
    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            # create ICMP socket, connect to destination IP, set timeout and time-to-live
            icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

            try:
                # create ICMP ping packet, record the time delay of getting response detect timeout
                icmp_socket.sendto(build_packet(), (destAddr, 1))
                recPacket, addr = icmp_socket.recvfrom(1024)
                ip_version = bin(struct.unpack('@B', recPacket[0:1])[0])[2:].zfill(8)[:4]
                if int(ip_version, 2) == 4:
                    time_sent = struct.unpack('@d', recPacket[28:])[0]
                    RTT = time.time() - time_sent
                    print('RTT: {:.3f}s'.format(RTT))
            except:
                continue
            else:
                # parse and handle different response type
                if int(ip_version, 2) == 4:
                    icmp_header = recPacket[20:28]
                    icmp_type, icmp_code, icmp_chechsum, icmp_id, icmp_seq = struct.unpack('@BBHHH', icmp_header)
                    if icmp_type == 3:
                        raise('destination unreachable')
                    elif icmp_type != 0:
                        raise('type error')

                # Hint: use wireshark to get the byte location of the response type

            finally:
                # close the socket
                icmp_socket.close()


if __name__ == "__main__":
    get_route(sys.argv[1])
