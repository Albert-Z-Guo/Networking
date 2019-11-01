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
        self.start_time = time.time()

    def new_packet(self, packet_byte_array):
        packet_seq_num = self.packet_seq_num.to_bytes(2, byteorder='big')
        # packet_byte_array = packet_seq_num + packet_byte_array 
        packet_byte_array[0:0] = packet_seq_num # insert sequence number at the beginning
        checksum = sum(packet_byte_array).to_bytes(2, byteorder='big')
        packet_byte_array += checksum # append checksum
        self.buffer.append(packet_byte_array)
        print('storing packet:', int.from_bytes(packet_byte_array[:2], byteorder='big'))
        self.packet_seq_num += 1

    def check_time(self):
        # if timeout
        if time.time() - self.start_time > 0.5:
            print('current time diff:', time.time() - self.start_time)
            print('timed out')
            self.start_time = time.time() # start timer
            # resend all data in window
            for i in range(self.base, self.next_packet_seq_num, 1):
                print('resending packet:', int.from_bytes(self.buffer[i-1][:2], byteorder='big'), self.buffer[i-1])
                self.my_tunnel.magic_send(bytearray(self.buffer[i-1]))

    def receive(self, packet_byte_array):
        ack_seq_num = packet_byte_array[:2]
        ack_payload = packet_byte_array[2:-2]
        checksum = packet_byte_array[-2:]

        # if ack is not corrupted
        if sum(packet_byte_array[:-2]).to_bytes(2, byteorder='big') == checksum:
            self.base = int.from_bytes(ack_seq_num, byteorder='big') + 1
            print('base now            :', self.base)
            if self.base == self.next_packet_seq_num:
                pass # stop timer
            else:
                self.start_time = time.time() # start timer
        # if ack is corrupted
        else:
            print('checksum:', int.from_bytes(checksum, byteorder='big'))
            print('data sum:', sum(packet_byte_array[:-2]))
            print('ack corrupted')

    def run(self):
        while not self.die:
            # if data is available to send
            if self.next_packet_seq_num - 1 < len(self.buffer):
                # send data if the next available sequence number is within window
                if self.next_packet_seq_num < self.base + self.window_size:    
                    print('sending packet...\tbase:', self.base, '\tnext_packet_seq_num:', self.next_packet_seq_num)
                    data = self.buffer[self.next_packet_seq_num-1]
                    # print('sent:', int.from_bytes(data[:2], byteorder='big'), data[2:-2])
                    self.my_tunnel.magic_send(bytearray(data))
                    if self.base == self.next_packet_seq_num:
                        self.start_time = time.time() # start timer
                    self.next_packet_seq_num += 1

            self.check_time()

    def join(self):
        self.die = True
        super().join()
