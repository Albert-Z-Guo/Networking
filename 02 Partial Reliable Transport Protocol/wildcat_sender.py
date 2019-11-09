import binascii
import copy
import math
import time
import threading

import common

class wildcat_sender(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_sender, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        self.buffer = {} # buffer of data to send
        self.packet_seq_num = 1
        self.next_packet_seq_num = 1
        self.base = 1 # window base
        self.packet_times = {} # packet times
        self.acks = set() # packet acknowledgements
        self.timeout_threshold = 0.5

    # 16 bit cyclic redundancy check (CRC) for 2-bit error (note that sending and receiving each may introduce 1 bit error)
    def crc_check(self, data_bytes, remainder_bytes):
        check_bin = bin(int.from_bytes(data_bytes, byteorder='big'))[2:] + bin(int.from_bytes(remainder_bytes, byteorder='big'))[2:].zfill(16)
        return binascii.crc_hqx(int(check_bin, 2).to_bytes(math.ceil(len(check_bin) / 8), byteorder='big'), 0) == 0

    def new_packet(self, packet_byte_array):
        packet = copy.copy(packet_byte_array) # make a copy so that it does not modify the original bytearray object
        packet_seq_num = (self.packet_seq_num % 65536).to_bytes(2, byteorder='big')
        packet[0:0] = packet_seq_num # insert sequence number in bytearray
        checksum = binascii.crc_hqx(packet, 0).to_bytes(2, byteorder='big')
        packet += checksum # append checksum
        self.buffer[self.packet_seq_num] = packet
        self.packet_seq_num += 1

    def check_time(self):
        for packet_num in range(self.base, self.base+self.window_size):
            # check unacknowledged packets' times
            if (packet_num not in self.acks) and (packet_num in self.packet_times) and (time.time() - self.packet_times[packet_num] > self.timeout_threshold):
                self.my_tunnel.magic_send(copy.copy(self.buffer[packet_num])) # resend packet
                self.packet_times[packet_num] = time.time() # start timer
                print('resending packet:', int.from_bytes(self.buffer[packet_num][:2], byteorder='big'))

    def receive(self, packet_byte_array):
        # if ack is not corrupted
        if self.crc_check(packet_byte_array[:-2], packet_byte_array[-2:]):
            ack_seq_num = int.from_bytes(packet_byte_array[:2], byteorder='big')
            
            # if sequence number wrap-around happens
            if ack_seq_num < self.base - self.window_size*2:
                ack_seq_num += (self.base + self.window_size) // 65536 * 65536

            # if packet is in the window
            if self.base <= ack_seq_num < self.base + self.window_size:
                self.acks.add(ack_seq_num) # mark packet as received
                print('\t\t\t\t\tpacket {} received'.format(ack_seq_num))
                # self.packet_times[ack_seq_num] = time.time() # update time
                if ack_seq_num == self.base:
                    self.base += 1
                    # move base forward to the unacknowledged packet with the smallest sequence number
                    while self.base in self.acks:
                        self.base += 1
                        print('sender base now:', self.base)
            else:
                print('sender base: {} \tpacket {} ack outside window'.format(self.base, ack_seq_num))
        # if ack is corrupted
        else:
            print('ack corrupted')
            self.my_tunnel.magic_send(copy.copy(self.buffer[self.base])) # resend base packet

    def run(self):
        while not self.die:
            # if data is available to send
            if self.next_packet_seq_num - 1 < len(self.buffer):
                # send data if the next available sequence number is within window
                if self.next_packet_seq_num < self.base + self.window_size:    
                    print('sender base:', self.base, 'sending packet:', self.next_packet_seq_num)
                    data = self.buffer[self.next_packet_seq_num]
                    self.my_tunnel.magic_send(copy.copy(data))
                    self.packet_times[self.next_packet_seq_num] = time.time() # time individual packet
                    self.next_packet_seq_num += 1

            self.check_time()

    def join(self):
        self.die = True
        super().join()
