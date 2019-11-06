import inspect
from multiprocessing import Process
import time
import unittest

import common
import start_receiver
import start_sender
import wildcat_receiver
import wildcat_sender


class sender:
    def __init__(self, ip, port, allowed_lost, window_size, loss_rate, corrupt_rate):
        self.my_tunnel = common.magic_tunnel(loss_rate, corrupt_rate)
        self.my_logger = common.logger()
        self.my_wildcat_sender = wildcat_sender.wildcat_sender(allowed_lost, window_size, self.my_tunnel, self.my_logger)
        self.my_wildcat_sender.start()
        self.my_tunnel.my_recv = self.my_wildcat_sender.receive
        self.udp_sender = start_sender.UDP_sender(ip, port, self.my_tunnel)
        self.udp_sender.start()
    
    def send(self, pkt_byte_array):
        self.my_wildcat_sender.new_packet(pkt_byte_array)
    
    def stop(self):
        self.my_wildcat_sender.join()
        self.udp_sender.join()


class receiver:
    def __init__(self, port, allowed_lost, window_size, loss_rate, corrupt_rate, log_file):
        self.my_tunnel = common.magic_tunnel(loss_rate, corrupt_rate)
        self.my_logger = common.logger(log_file)
        self.my_wildcat_receiver = wildcat_receiver.wildcat_receiver(allowed_lost, window_size, self.my_tunnel, self.my_logger)
        self.my_wildcat_receiver.start()
        self.my_tunnel.my_recv = self.my_wildcat_receiver.receive
        self.udp_receiver = start_receiver.UDP_receiver(port, self.my_tunnel)
        self.udp_receiver.start()
    
    def get_commit_list(self):
        return self.my_logger.get_commit_list()
    
    def stop(self):
        self.my_wildcat_receiver.join()
        self.udp_receiver.join()

def run_sender(ip, port, allowed_lost, window_size, loss_rate, corrupt_rate, send_list, timeout):
    my_sender = sender(ip, port, allowed_lost, window_size, loss_rate, corrupt_rate)

    for pkt in send_list:
        my_sender.send(pkt)

    time.sleep(timeout)
    my_sender.stop()

def run_test(ip, port, allowed_lost, window_size, loss_rate, corrupt_rate, send_list, timeout, log_file):
    my_receiver = receiver(port, allowed_lost, window_size, loss_rate, corrupt_rate, log_file)
    
    p = Process(target=run_sender, args=(ip, port, allowed_lost, window_size, loss_rate, corrupt_rate, send_list, timeout,))
    p.start()
    
    time.sleep(timeout)
    commit_list = my_receiver.get_commit_list()
    my_receiver.stop()
    p.join()
    return commit_list

'''
class TestReliableNoLossNoCorrupt(unittest.TestCase):
    loss_rate = 0
    corrupt_rate = 0
    allowed_lost = 0
    window_size = 20
    ip = "localhost"
    port = 8000
    my_sender = None
    my_receiver = None

    def test_send_10_pkt(self):
        log_file = "log/" + str(self.__class__.__name__) + "_" + str(inspect.stack()[0][3]) + '.txt'
        timeout = 2
        pkt_num = 10
        send_list = []
        for i in range(pkt_num):
            send_list = send_list + [bytearray([i%256])]
        commit_list = run_test(self.ip, self.port, self.allowed_lost, self.window_size, self.loss_rate, self.corrupt_rate, send_list, timeout, log_file)
        print("Sent " + str(len(send_list)) + " packets, received " + str(len(commit_list)) + " packets")
        assert sorted(send_list) == sorted(commit_list)

    def test_send_100_pkt(self):
        log_file = "log/" + str(self.__class__.__name__) + "_" + str(inspect.stack()[0][3]) + '.txt'
        timeout = 8
        pkt_num = 100
        send_list = []
        for i in range(pkt_num):
            send_list = send_list + [bytearray([i%256])]
        commit_list = run_test(self.ip, self.port, self.allowed_lost, self.window_size, self.loss_rate, self.corrupt_rate, send_list, timeout, log_file)
        print("Sent " + str(len(send_list)) + " packets, received " + str(len(commit_list)) + " packets")
        assert sorted(send_list) == sorted(commit_list)
 

class TestReliableWithLossWithCorrupt(unittest.TestCase):
    loss_rate = 20
    corrupt_rate = 20
    allowed_lost = 0
    window_size = 20
    ip = "localhost"
    port = 8000
    my_sender = None
    my_receiver = None

    def test_send_100_pkt(self):
        log_file = "log/" + str(self.__class__.__name__) + "_" + str(inspect.stack()[0][3]) + '.txt'
        timeout = 40
        pkt_num = 100
        send_list = []
        for i in range(pkt_num):
            send_list = send_list + [bytearray([i%256])]
        commit_list = run_test(self.ip, self.port, self.allowed_lost, self.window_size, self.loss_rate, self.corrupt_rate, send_list, timeout, log_file)
        print("Sent " + str(len(send_list)) + " packets, received " + str(len(commit_list)) + " packets")
        assert sorted(send_list) == sorted(commit_list)


class TestUnreliableWithLossWithCorrupt(unittest.TestCase):
    loss_rate = 20
    corrupt_rate = 20
    allowed_lost = 20
    window_size = 20
    ip = "localhost"
    port = 8000
    my_sender = None
    my_receiver = None

    def test_send_100_pkt(self):
        log_file = "log/" + str(self.__class__.__name__) + "_" + str(inspect.stack()[0][3]) + '.txt'
        timeout = 30
        pkt_num = 100
        send_list = []
        for i in range(pkt_num):
            send_list = send_list + [bytearray([i%256])]
        commit_list = run_test(self.ip, self.port, self.allowed_lost, self.window_size, self.loss_rate, self.corrupt_rate, send_list, timeout, log_file)
        print("Sent " + str(len(send_list)) + " packets, received " + str(len(commit_list)) + " packets")
        assert (len(commit_list) / len(send_list)) * 100 > (100 - self.allowed_lost)
'''

class TestReliableWithoutLossWithCorruptAtScale(unittest.TestCase):
    loss_rate = 0
    corrupt_rate = 5
    allowed_lost = 0
    window_size = 20
    ip = "localhost"
    port = 8000
    my_sender = None
    my_receiver = None

    def test_send_66000_pkt(self):
        log_file = "log/" + str(self.__class__.__name__) + "_" + str(inspect.stack()[0][3]) + '.txt'
        timeout = 60 * 60 * 0.9
        pkt_num = 66000
        # timeout = 150
        # pkt_num = 100
        send_list = []
        for i in range(pkt_num):
            send_list = send_list + [bytearray([i % 256])]
        commit_list = run_test(self.ip, self.port, self.allowed_lost, self.window_size, self.loss_rate, self.corrupt_rate, send_list, timeout, log_file)
        print("Sent " + str(len(send_list)) + " packets, received " + str(len(commit_list)) + " packets")

        with open('log/send_list.txt', 'w') as f:
            for pkt in send_list:
                f.write('{}\n'.format(pkt))

        assert sorted(send_list) == sorted(commit_list)

if __name__ == '__main__':
    unittest.main()