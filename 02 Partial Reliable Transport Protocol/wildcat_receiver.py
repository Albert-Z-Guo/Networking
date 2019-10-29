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
        self.window_starting_position = 1

    def receive(self, packet_byte_array):
        print(packet_byte_array)
        seq_num = packet_byte_array[:2]
        data = packet_byte_array[2:-2]
        checksum = packet_byte_array[-2:]
        print(seq_num, data, checksum)

        if sum(data).to_bytes(2, byteorder='big') == checksum:
            ack = self.window_starting_position.to_bytes(2, byteorder='big') + (1).to_bytes(1, byteorder='big') + packet_byte_array[-2:]
            print('no corruption')
        else:
            ack = self.window_starting_position.to_bytes(2, byteorder='big') + (0).to_bytes(1, byteorder='big') + packet_byte_array[-2:]
            print('data corrupted')

        self.my_tunnel.magic_send(ack)
        self.my_logger.commit(packet_byte_array)


    def run(self):
        while not self.die:
            time.sleep(2)

    def join(self):
        self.die = True
        super().join()
