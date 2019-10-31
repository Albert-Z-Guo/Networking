import time
import queue

import common
import threading

class wildcat_sender(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_sender, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        # add as needed
        self.buffer = []
        self.packet_seq_num = 1
        self.next_packet_seq_num = 1
        self.base = 1
        self.ack_seq_num = None
        self.time = 0

    def new_packet(self, packet_byte_array):
        packet_seq_num = self.packet_seq_num.to_bytes(2, byteorder='big')
        checksum = sum(packet_byte_array).to_bytes(2, byteorder='big')
        # print('new packet')
        # print('packet_seq_num:', packet_seq_num)
        # print('checksum:', checksum)
        packet_byte_array[0:0] = packet_seq_num # insert sequence number at the beginning
        packet_byte_array += checksum # append checksum
        # print('new:', packet_byte_array)
        self.buffer.append(packet_byte_array)
        self.packet_seq_num += 1

    def timeout(self):
        if time.time() - self.time > 0.5:
            self.time = time.time() # start timer
            # if data is available to send
            if self.next_packet_seq_num-1 < len(self.buffer):
                print('timed out')
                # resend all data in window
                for i in range(self.base, self.next_packet_seq_num):
                    self.my_tunnel.magic_send(self.buffer[i-1])

    def receive(self, packet_byte_array):
        ack_seq_num = packet_byte_array[:2]
        ack_payload = packet_byte_array[2:-2]
        checksum = packet_byte_array[-2:]

        # if ack is not corrupted
        if sum(ack_payload).to_bytes(2, byteorder='big') == checksum:
            self.ack_seq_num = int.from_bytes(ack_seq_num, byteorder='big')
            self.base = self.ack_seq_num + 1
            if self.base == self.next_packet_seq_num:
                self.time = 0 # stop timer
            else:
                self.time = time.time() # start timer
        # if ack is corrupted
        else:
            print('ack corrupted')

    def run(self):
        while not self.die:
            # if data is available to send
            if self.next_packet_seq_num-1 < len(self.buffer):
                # send data
                if self.next_packet_seq_num < self.base + self.window_size:    
                    data = self.buffer[self.next_packet_seq_num-1]
                    # print('sent:', data)
                    self.my_tunnel.magic_send(data)
                    if self.base == self.next_packet_seq_num:
                        self.time = time.time() # start timer
                    self.next_packet_seq_num += 1

            self.timeout()    

    def join(self):
        self.die = True
        super().join()
