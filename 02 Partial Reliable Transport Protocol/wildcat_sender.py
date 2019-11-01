import time

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
        self.buffer = {}
        self.packet_seq_num = 1
        self.next_packet_seq_num = 1
        self.base = 1
        self.packet_times = {}
        self.acks = set()

    def new_packet(self, packet_byte_array):
        packet_seq_num = self.packet_seq_num.to_bytes(2, byteorder='big')
        packet_byte_array[0:0] = packet_seq_num # insert sequence number in bytearray
        checksum = sum(packet_byte_array).to_bytes(2, byteorder='big')
        packet_byte_array += checksum # append checksum
        self.buffer[self.packet_seq_num] = packet_byte_array 
        self.packet_seq_num += 1

    def check_time(self):
        for packet_num in range(self.base, self.base+self.window_size):
            if packet_num in self.packet_times and time.time() - self.packet_times[packet_num] > 0.5: # if timeout
                self.my_tunnel.magic_send(bytearray(self.buffer[packet_num])) # resend packet
                self.packet_times[packet_num] = time.time() # start timer
                print('resending packet:', int.from_bytes(self.buffer[packet_num][:2], byteorder='big'))

    def receive(self, packet_byte_array):
        ack_seq_num = int.from_bytes(packet_byte_array[:2], byteorder='big') 
        checksum = int.from_bytes(packet_byte_array[-2:], byteorder='big')
        # if ack is not corrupted
        if sum(packet_byte_array[:-2]) == checksum:
            if self.base <= ack_seq_num < self.base + self.window_size: # if packet is in the window
                self.acks.add(ack_seq_num) # mark packet as received
                self.packet_times[ack_seq_num] = time.time() # update time
                if ack_seq_num == self.base:
                    self.base += 1
                    # move base forward to the unacknowledged packet with the smallest sequence number
                    while self.base in self.acks:
                        self.base += 1
                        print('base now:', self.base)
        # if ack is corrupted
        else:
            print('ack corrupted')
            self.my_tunnel.magic_send(bytearray(self.buffer[self.base])) # resend base packet

    def run(self):
        while not self.die:
            # if data is available to send
            if self.next_packet_seq_num - 1 < len(self.buffer):
                # send data if the next available sequence number is within window
                if self.next_packet_seq_num < self.base + self.window_size:    
                    print('sending packet...\tbase:', self.base, '\tnext_packet_seq_num:', self.next_packet_seq_num)
                    data = self.buffer[self.next_packet_seq_num]
                    self.my_tunnel.magic_send(bytearray(data))
                    self.packet_times[self.next_packet_seq_num] = time.time() # time individual packet
                    self.next_packet_seq_num += 1

            self.check_time()

    def join(self):
        self.die = True
        super().join()
