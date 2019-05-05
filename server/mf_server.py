import socket
import json

server_port = 4918
communication_port = 4919

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', server_port))
s.settimeout(0.2)

my_ip = socket.gethostbyname(socket.gethostname())

def send_discover_response(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    msg = {'type': 'discovery_response', 'server_ip': my_ip}
    print('Sending response: ' + str(msg))
    s.sendto(json.dumps(msg).encode(), (ip, port))

def handle_msg(data):
    t = data['type']
    if t == 'discovery':
        print('Received discovery request from ' + str(data['from_ip']))
        send_discover_response(data['from_ip'], communication_port)

running = True
try:
    while(running):
        try:
            m = s.recvfrom(4096)
            print(str(m[1]) + ': ' + str(m[0]))
            try:
                msg = json.loads(m[0])
                msg['from_ip'] = m[1][0]
                msg['from_port'] = m[1][1]
                handle_msg(msg)
            except json.decoder.JSONDecodeError:
                print("Invalid JSON received")
        except socket.timeout:
            pass
        except (OSError) as e:
            print(e)
except KeyboardInterrupt:
    running = False
    print('Exiting...')
