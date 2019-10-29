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
        self.base = 1
        self.nextseqnum = 1
        self.timer = threading.Timer(5.0, self.timeout)


    def new_packet(self, packet_byte_array):
        seq_num = self.nextseqnum.to_bytes(2, byteorder='big')
        checksum = sum(packet_byte_array).to_bytes(2, byteorder='big')
        print('seq_num:', seq_num)
        print('checksum:', checksum)
        packet_byte_array[0:0] = seq_num # insert sequence number at the beginning
        packet_byte_array += checksum # append checksum
        self.my_tunnel.magic_send(packet_byte_array)


    def receive(self, packet_byte_array):
        print(packet_byte_array)


    def run(self):
        while not self.die:
            time.sleep(2)
            # if self.nextseqnum < self.base + self.window_size:
            #     print('sending...')
            #     self.my_tunnel.magic_send(self.new_packet(packet_byte_array))
            #     time.sleep(2)
            #     break


    def join(self):
        self.die = True
        super().join()
