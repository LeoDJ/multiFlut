import socket
import json
import time
import traceback
import threading
import sys

server_port = 4918
communication_port = 4919
heartbeat_check_interval = 1.0  # s
heartbeat_timeout = 5.0  # s

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.2)  # only wait for 0.2s so network thread is exitable
sock.bind(('', server_port))

my_ip = socket.gethostbyname(socket.gethostname())
clients = {}
running = True


def check_timeout():
    if not running:
        return
    threading.Timer(heartbeat_check_interval, check_timeout).start()
    for ip in list(clients):
        if clients[ip]['last_seen'] < time.time() - heartbeat_timeout:
            del clients[ip]
            print("Timeout from client " + ip)


def send_discover_response(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    msg = {'type': 'discovery_response', 'server_ip': my_ip}
    print('Sending response: ' + str(msg))
    sock.sendto(json.dumps(msg).encode(), (ip, port))


def handle_msg(data):
    t = data['type']
    global clients
    if t == 'discovery':
        print('Received discovery request from ' + str(data['from_ip']))
        send_discover_response(data['from_ip'], communication_port)
    elif t == 'heartbeat':
        clients[data['from_ip']] = {'last_seen': time.time()}
        # print(clients)
    elif t == 'disconnect':
        try:
            del clients[data['from_ip']]
        except KeyError:
            pass
        print("Disconnect from client " + data['from_ip'])
        # print(clients)


def network_task():
    while(running):
        try:
            m = sock.recvfrom(4096)
            print(str(m[1]) + ': ' + str(m[0]))
            try:
                msg = json.loads(m[0])
                msg['from_ip'] = m[1][0]
                msg['from_port'] = m[1][1]
                handle_msg(msg)
            except json.decoder.JSONDecodeError:
                print("Invalid JSON received")
        except (socket.timeout, BlockingIOError, ConnectionResetError):
            pass
        except (OSError) as e:
            # print(e.type, e)
            traceback.print_exc()


def main():
    global running
    try:
        print("Running multiFlut server at " +
              str(my_ip) + ":" + str(server_port))
        threading.Thread(target=network_task).start()
        check_timeout()  # start checking for timeouted clients
        while(running):
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        running = False
        print('Exiting...')
        print(clients)
        sys.exit()


if __name__ == "__main__":
    main()
