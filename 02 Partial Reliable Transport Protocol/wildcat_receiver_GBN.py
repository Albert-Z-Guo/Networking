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
        self.expected_packet_seq_num = 1

    def receive(self, packet_byte_array):
        packet_seq_num = int.from_bytes(packet_byte_array[:2], byteorder='big')
        checksum = int.from_bytes(packet_byte_array[-2:], byteorder='big')

        # if data is not corrupted
        if sum(packet_byte_array[:-2]) == checksum:
            # if the packet has expected sequence number
            print('expected packet seq num:', self.expected_packet_seq_num)
            if packet_seq_num == self.expected_packet_seq_num:
                # send ack back to sender
                ack_payload = self.expected_packet_seq_num.to_bytes(2, byteorder='big') + (1).to_bytes(1, byteorder='big')
                ack = ack_payload + sum(ack_payload).to_bytes(2, byteorder='big') # append checksum
                print('ack_seq_num sent:', self.expected_packet_seq_num)
                self.my_tunnel.magic_send(bytearray(ack))
                self.my_logger.commit(copy.copy(packet_byte_array[2:-2])) # deliver data
                self.expected_packet_seq_num += 1
        # if data is corrupted
        else:
            print('received packet corrupted')

    def run(self):
        while not self.die:
            time.sleep(2)

    def join(self):
        self.die = True
        super().join()