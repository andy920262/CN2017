import socket
import random
import pickle
import argparse

class Agent:
    def __init__(self, ip='127.0.0.1', port=7123, loss_rate=0.0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.loss_rate = loss_rate
    
    def send(self, addr, content):
        self.socket.sendto(pickle.dumps(content), addr)

    def recv(self):
        data, addr = self.socket.recvfrom(4096)
        return pickle.loads(data)
    
    def listen(self):
        self.socket.bind((self.ip, self.port))
        total_packet, drop_packet = 0, 0

        while True:
            packet = self.recv()

            if packet['type'] == 'ext':
                self.send(packet['dst_addr'], packet)
                continue

            if packet['type'] == 'data':
                total_packet += 1
            if packet['type'] == 'data' or packet['type'] == 'ack':
                print('get\t{}\t#{}'.format(packet['type'], packet['seq']))
            else:
                print('get\t{}'.format(packet['type']))

            if packet['type'] == 'data' and random.random() < self.loss_rate:
                drop_packet += 1
                print('drop\t{}\t#{},\tloss rate = {:.4f}'.format(packet['type'], packet['seq'], drop_packet / total_packet))
            else:
                if packet['type'] == 'data' or packet['type'] == 'ack':
                    print('fwd\t{}\t#{}'.format(packet['type'], packet['seq']))
                else:
                    print('fwd\t{}'.format(packet['type']))
                self.send(packet['dst_addr'], packet)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=7123)
    parser.add_argument('--loss', type=float, default=0.0)
    arg = parser.parse_args()
    agent = Agent(ip=arg.ip, port=arg.port, loss_rate=arg.loss)
    agent.listen()
            
