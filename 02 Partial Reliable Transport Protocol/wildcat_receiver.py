import time

import common
import threading

class wildcat_receiver(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_receiver, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        # add as needed
        self.base = 1
        self.buffer = {}

    def receive(self, packet_byte_array):
        packet_seq_num = int.from_bytes(packet_byte_array[:2], byteorder='big')
        checksum = int.from_bytes(packet_byte_array[-2:], byteorder='big')

        # if data is not corrupted
        if sum(packet_byte_array[:-2]) == checksum:
            ack_payload = packet_seq_num.to_bytes(2, byteorder='big') + (1).to_bytes(1, byteorder='big')
            ack = ack_payload + sum(ack_payload).to_bytes(2, byteorder='big')

            if self.base <= packet_seq_num < self.base + self.window_size:
                self.my_tunnel.magic_send(bytearray(ack))
                print('ack_seq_num sent:', packet_seq_num)
                # if the packet's sequence number is the base, this packet and 
                # any previously buffered and consecutively numbered packets are delivered
                if packet_seq_num == self.base:
                    self.my_logger.commit(bytearray(packet_byte_array))
                    self.base += 1
                    while self.base in self.buffer.keys():
                        self.my_logger.commit(bytearray(self.buffer[self.base]))
                        del self.buffer[self.base]
                        self.base += 1
                # buffer packet
                else:
                    self.buffer[packet_seq_num] = packet_byte_array
            
            # send duplicated ack
            if packet_seq_num < self.base:
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
