import socket
import sys
import time
import pickle
import argparse

class Sender:
    def __init__(self, src_addr=('127.0.0.1', 7122), agent_addr=('127.0.0.1', 7123),
            dst_addr=('127.0.0.1', 7124), timeout=1, thres=32):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.init_thres = thres
        self.src_addr = src_addr
        self.agent_addr = agent_addr
        self.dst_addr = dst_addr 
        self.timeout = timeout

    def send(self, data):
        self.socket.sendto(pickle.dumps(data), self.agent_addr)
    
    def recv(self):
        data, addr = self.socket.recvfrom(4096)
        return pickle.loads(data)
    
    def load_file(self, file_path):
        data = open(file_path, 'rb').read()
        data = [b''] + [data[i : min(len(data), i + 1024)] for i in range(0, len(data), 1024)]
        return data

    def send_file(self, file_path):
        data = self.load_file(file_path)
        base, win_size, thres = 1, 1, self.init_thres
        data_sent = set()
        self.socket.bind(self.src_addr)
        self.socket.settimeout(self.timeout)
        done = False
       
        file_ext = file_path.split('.')[-1]
        packet = {
                'src_addr': self.src_addr,
                'dst_addr': self.dst_addr,
                'type': 'ext',
                'data': file_ext}
        self.send(packet)

        while not done:
            send_cnt = 0
            for i in range(base, min(base + win_size, len(data))):
                if i in data_sent:
                    print('resnd\tdata\t#{},\twinSize = {}'.format(i, win_size))
                else:
                    print('send\tdata\t#{},\twinSize = {}'.format(i, win_size))
                packet = {
                        'src_addr': self.src_addr,
                        'dst_addr': self.dst_addr,
                        'type': 'data',
                        'seq': i,
                        'data': data[i]}
                self.send(packet)
                data_sent.add(i)
                send_cnt += 1
            
            loss = False
            recv_cnt = 0
            
            while True:
                try:
                    packet = self.recv()
                    print('recv\tack\t#{}'.format(packet['seq']))
                    if packet['seq'] == base:
                        base += 1
                        recv_cnt += 1
                    if recv_cnt == send_cnt:
                        break
                except socket.timeout:
                    loss = True
                    break
            
            if loss or (recv_cnt != send_cnt):
                win_size, thres = 1, int(max(win_size / 2, 1))
                print('time\tout,\tthreshold = {}'.format(thres))
            else:
                win_size = win_size * 2 if win_size < thres else win_size + 1

            if base >= len(data):
                packet = {
                        'src_addr': self.src_addr,
                        'dst_addr': self.dst_addr,
                        'type': 'fin'}
                self.send(packet)
                print('send\tfin')
                done = True

        packet = self.recv()
        if packet['type'] == 'finack':
            print('recv\tfinack')
        else:
            print('Error: wrong packet type.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--src_ip', default='127.0.0.1')
    parser.add_argument('--src_port', type=int, default=7122)
    parser.add_argument('--agent_ip', default='127.0.0.1')
    parser.add_argument('--agent_port', type=int, default=7123)
    parser.add_argument('--dst_ip', default='127.0.0.1')
    parser.add_argument('--dst_port', type=int, default=7124)
    parser.add_argument('--threshold', type=int, default=16)
    parser.add_argument('--timeout', type=float, default=1.0)
    arg = parser.parse_args()
    sender = Sender(
            src_addr=(arg.src_ip, arg.src_port),
            agent_addr=(arg.agent_ip, arg.agent_port),
            dst_addr=(arg.dst_ip, arg.dst_port),
            timeout=arg.timeout,
            thres=arg.threshold)
    sender.send_file(arg.file)
