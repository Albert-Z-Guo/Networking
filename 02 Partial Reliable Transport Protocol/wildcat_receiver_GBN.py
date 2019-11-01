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

        # if data is not corrupted
        if sum(packet_byte_array[:-2]).to_bytes(2, byteorder='big') == checksum:
            # if the packet has expected sequence number
            print('expected packet seq num:', self.expected_packet_seq_num)
            if int.from_bytes(packet_seq_num, byteorder='big') == self.expected_packet_seq_num:
                # send ack back to sender
                ack_payload = self.expected_packet_seq_num.to_bytes(2, byteorder='big') + (1).to_bytes(1, byteorder='big')
                ack = ack_payload + sum(ack_payload).to_bytes(2, byteorder='big')
                print('ack_seq_num sent    :', self.expected_packet_seq_num)
                self.my_tunnel.magic_send(bytearray(ack))
                self.my_logger.commit(bytearray(packet_byte_array)) # deliver data
                self.expected_packet_seq_num += 1
        # if data is corrupted
        else:
            ack_payload = (0).to_bytes(1, byteorder='big')
            print('received packet corrupted:', self.expected_packet_seq_num)

    def run(self):
        while not self.die:
            time.sleep(2)

    def join(self):
        self.die = True
        super().join()