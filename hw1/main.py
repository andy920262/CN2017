import socket
import time

IRCSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
channel = '#CN7122'
username = 'robot'
hostname = 'CN2017'
servername = 'CN2017'
realname = 'Robot'
nickname = 'ROBOT_7122'

def send_msg(msg):
    IRCSocket.send('PRIVMSG {} :{}\n'.format(channel, msg).encode())

def valid_ip(ip):
    return __valid_ip(str(ip), 0, [])

def __valid_ip(ip, x, valid):
    if x == 4:
        if len(ip) == 0:
            return ['.'.join(valid)]
        return []
    ret = []
    for i in range(1, len(ip) + 1):
        if int(ip[:i]) > 255 or (i > 1 and int(ip[0]) == 0):
            break
        ret += __valid_ip(ip[i:], x + 1, valid + [ip[:i]])
    return ret

if __name__ == '__main__':

    with open('config', 'r') as config:
        conf = config.read().split('=')
        if conf[0] == 'CHAN':
            channel = conf[1].replace('\'', '').replace('\n', '')

    IRCSocket.connect(('irc.freenode.net', 6667))
    IRCSocket.send('USER {} {} {} {}\n'.format(username, hostname, servername, realname).encode())
    IRCSocket.send('NICK {}\n'.format(nickname).encode())
    IRCSocket.send('JOIN {}\n'.format(channel).encode())
    send_msg('Hello! I am robot.')

    while True:
        try:
            msg = IRCSocket.recv(4096).decode()
        except ConnectionResetError:
            continue
        print(msg)
        msg = msg.split(' ')
        if len(msg) > 1 and msg[1] == 'PRIVMSG':
            msg = msg[3:]
            op = msg[0][1:]
            if op == '@repeat':
                send_msg(' '.join(msg[1:]))
            if op == '@convert':
                try:
                    if msg[1][:2] == '0x':
                        send_msg(int(msg[1], 16))
                    else:
                        send_msg(hex(int(msg[1])))
                except ValueError:
                    print('Invalid input.')

            if op == '@ip':
                try:
                    ret = valid_ip(int(msg[1]))
                except ValueError:
                    print('Invalid input.')
                    ret = []
                send_msg(len(ret))
                for i in ret:
                    send_msg(i)
                    time.sleep(1)


            if op == '@help\r\n':
                send_msg('@repeat <Message>')
                send_msg('@convert <Number>')
                send_msg('@ip <String>')

