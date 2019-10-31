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
        self.expected_packet_seq_num = 1

    def receive(self, packet_byte_array):
        packet_seq_num = packet_byte_array[:2]
        data = packet_byte_array[2:-2]
        checksum = packet_byte_array[-2:]
        # print(packet_seq_num, data, checksum)

        # check if data is corrupted
        if sum(data).to_bytes(2, byteorder='big') == checksum:
            ack_payload = (1).to_bytes(1, byteorder='big')
            self.expected_packet_seq_num += 1
            self.my_logger.commit(packet_byte_array)
        else:
            ack_payload = (0).to_bytes(1, byteorder='big')
            print('data corrupted')

        # send ack back to sender
        ack = self.expected_packet_seq_num.to_bytes(2, byteorder='big') + ack_payload + sum(ack_payload).to_bytes(2, byteorder='big')
        self.my_tunnel.magic_send(bytearray(ack))

    def run(self):
        while not self.die:
            time.sleep(2)

    def join(self):
        self.die = True
        super().join()
