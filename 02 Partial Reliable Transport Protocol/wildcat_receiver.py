import copy
import time
import threading

import common


class wildcat_receiver(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_receiver, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        # add as needed
        self.base = 1 # window base
        self.buffer = {} # buffer of received packets in window

    def receive(self, packet_byte_array):
        packet_seq_num = int.from_bytes(packet_byte_array[:2], byteorder='big')
        checksum = int.from_bytes(packet_byte_array[-2:], byteorder='big')
        # if data is not corrupted
        if sum(packet_byte_array[:-2]) == checksum:
            ack_payload = packet_seq_num.to_bytes(2, byteorder='big') + (1).to_bytes(1, byteorder='big')
            ack = ack_payload + sum(ack_payload).to_bytes(2, byteorder='big')
            
            # if sequence number wrap-around happens
            if packet_seq_num < self.base - self.window_size*2:
                packet_seq_num += (self.base + self.window_size) // 65536 * 65536
            
            # if packet is in the window
            if self.base <= packet_seq_num < self.base + self.window_size:
                self.my_tunnel.magic_send(bytearray(ack))
                print('ack_seq_num sent:', packet_seq_num)
                # if the packet's sequence number is the base, this packet and 
                # any previously buffered and consecutively numbered packets are delivered
                if packet_seq_num == self.base:
                    self.my_logger.commit(copy.copy(packet_byte_array[2:-2]))
                    self.base += 1
                    while self.base in self.buffer.keys():
                        self.my_logger.commit(copy.copy(self.buffer[self.base][2:-2]))
                        del self.buffer[self.base] # save memory
                        self.base += 1
                        print('receiver base now:', self.base)
                # buffer packet
                else:
                    print('buffer received packet:', packet_seq_num)
                    self.buffer[packet_seq_num] = copy.copy(packet_byte_array)
            
            # send duplicated ack
            elif self.base - self.window_size <= packet_seq_num < self.base:
                self.my_tunnel.magic_send(bytearray(ack))
        # if data is corrupted
        else:
            print('received packet corrupted')

    def run(self):
        while not self.die:
            time.sleep(2)

    def join(self):
        self.die = True
        super().join()
