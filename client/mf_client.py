import socket
import json
import time
import traceback
import threading

server_port = 4918
communication_port = 4919
heartbeat_interval = 1.0  # s

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.settimeout(0.2)  # only wait for 0.2s so network thread is exitable
sock.bind(('', communication_port))

server_ip = ''
my_ip = socket.gethostbyname(socket.gethostname())
running = True
last_heartbeat = 0


def send_heartbeat():
    if not running:
        return
    threading.Timer(heartbeat_interval, send_heartbeat).start()
    if server_ip:
        msg = json.dumps({'type': 'heartbeat'}).encode()
        sock.sendto(msg, (server_ip, server_port))
    else:
        print("no server ip " + server_ip)


def send_discovery():
    msg = json.dumps({'type': 'discovery'}).encode()
    sock.sendto(msg, ('<broadcast>', server_port))


def send_disconnect():
    if server_ip:
        msg = json.dumps({'type': 'disconnect'}).encode()
        sock.sendto(msg, (server_ip, server_port))


def handle_msg(data):
    t = data['type']
    if t == 'discovery_response':
        global server_ip
        server_ip = data['server_ip']
        print('New server IP: ' + server_ip)


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
            except (json.decoder.JSONDecodeError, IndexError) as e:
                print("Invalid JSON received - " + str(e))
        except (socket.timeout, BlockingIOError, ConnectionResetError):
            pass
        except (OSError) as e:
            # print(e.type, e)
            traceback.print_exc()


def main():
    global running
    try:
        print("multiFlut client started at " +
              str(my_ip) + ":" + str(communication_port))
        threading.Thread(target=network_task).start()
        send_discovery()
        send_heartbeat()  # start heartbeat timer
        while(running):
            time.sleep(1)
    except KeyboardInterrupt:
        send_disconnect()
        running = False
        print('Exiting...')


if __name__ == "__main__":
    main()
