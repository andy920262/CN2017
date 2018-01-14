import socket
import pickle
import argparse

class Receiver:
    def __init__(self, host_addr=('127.0.0.1', 7124), agent_addr=('127.0.0.1', 7123), buffer_size=32):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host_addr = host_addr
        self.agent_addr = agent_addr
        self.buffer_size = buffer_size
   
    def recv(self):
        data, addr = self.socket.recvfrom(4096)
        return pickle.loads(data)
    
    def send(self, data):
        self.socket.sendto(pickle.dumps(data), self.agent_addr)
    
    def recv_file(self, file_path='result'):
        self.socket.bind(self.host_addr)
        last_seq = 0
        buf = []
        fd = open(file_path, 'wb')

        while True:
            packet = self.recv()

            if packet['type'] == 'ext':
                fd.close()
                fd = open(file_path + '.' + packet['data'], 'wb')
                continue

            if packet['type'] == 'fin':
                print('recv\tfin')
                packet = {
                        'src_addr': self.host_addr,
                        'dst_addr': packet['src_addr'],
                        'type': 'finack'}
                self.send(packet)
                print('send\tfinack')
                for d in buf:
                    fd.write(d)
                buf = []
                print('flush')
                break
            
            # Buffer overflow
            if len(buf) >= self.buffer_size:
                print('drop\t{}\t#{}'.format(packet['type'], packet['seq']))
                for d in buf:
                    fd.write(d)
                buf = []
                print('flush')
                continue

            if packet['seq'] == last_seq + 1:
                print('recv\t{}\t#{}'.format(packet['type'], packet['seq']))
                buf.append(packet['data'])
                last_seq = packet['seq']
            else:
                print('drop\t{}\t#{}'.format(packet['type'], packet['seq']))
            
            packet = {
                    'src_addr': self.host_addr,
                    'dst_addr': packet['src_addr'],
                    'type': 'ack',
                    'seq': last_seq}
            print('send\t{}\t#{}'.format(packet['type'], packet['seq']))
            self.send(packet)
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--ip', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=7124)
    parser.add_argument('--agent_ip', default='127.0.0.1')
    parser.add_argument('--agent_port', type=int, default=7123)
    parser.add_argument('--buffer_size', type=int, default=32)
    arg = parser.parse_args()
    receiver = Receiver(
            host_addr=(arg.ip, arg.port),
            agent_addr=(arg.agent_ip, arg.agent_port),
            buffer_size=arg.buffer_size)
    receiver.recv_file(arg.file)
