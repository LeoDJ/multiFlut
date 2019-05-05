import socket
import json

server_port = 4918
communication_port = 4919

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.settimeout(0.2)
sock.bind(('', communication_port))

server_ip = ''

def send_discovery():
    msg = json.dumps({'type': 'discovery'}).encode()
    sock.sendto(msg, ('<broadcast>', server_port))

def handle_msg(data):
    t = data['type']
    if t == 'discovery_response':
        server_ip = data['server_ip']
        print('New server IP: ' + server_ip)

running = True
try:
    send_discovery()
    while(running):
        try:
            m = sock.recvfrom(4096)
            print(str(m[1]) + ': ' + str(m[0]))
            try:
                msg = json.loads(m[0])
                msg['from_ip'] = m[1][0]
                msg['from_port'] = m[1][1]
                handle_msg(msg)
            except (json.decoder.JSONDecodeError, IndexError) as e:
                print("Invalid JSON received - " + str(e))
        except socket.timeout:
            pass
        except (OSError) as e:
            print(e)
except KeyboardInterrupt:
    running = False
    print('Exiting...')
