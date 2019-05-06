import socket
import json
import time
import traceback
import threading
import sys
import argparse
import re

server_port = 4918
communication_port = 4919
heartbeat_check_interval = 1.0  # s
heartbeat_timeout = 5.0  # s

sock = None
my_ip = ''
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


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("imageFile")

    parser.add_argument("-x", "--xoffset", type=int, default=0)
    parser.add_argument("-y", "--yoffset", type=int, default=0)
    # parser.add_argument("-t", "--threads", type=int, default=1,
    #                     help="number of threads for data sending")
    # parser.add_argument("-u", "--nocompression", action='store_const', const=True,
    #                     default=False, help="save cache file uncompressed")
    # parser.add_argument("-r", "--regenerate", action='store_const', const=True,
    #                     default=False, help="overwrite cached file")
    # parser.add_argument("-n", "--nocache", action='store_const', const=True,
    #                     default=False, help="disable writing cache file")
    # parser.add_argument("-a", "--algorithm", type=int, default=0,
    #                     help="algorithm selection 0=lineByLine, 1=randomPixel")

    args = parser.parse_args()
    return args

def get_canvas_size(ip, port): # returns tuple of x and y size
    tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmp_sock.settimeout(0.5)
    try:
        tmp_sock.connect((ip, port))
        tmp_sock.send(b"SIZE\n")
        size_str = tmp_sock.recv(4096)
        result = re.findall("SIZE (\d+) (\d+)", str(size_str))[0]
        return result
    except (ConnectionRefusedError, TimeoutError, socket.timeout):
            print("Connection to Pixelflut at " + str(ip) + ":" + str(port) + " failed or SIZE cmd not supported")

def main():
    global running, sock, my_ip
    args = parseArgs()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.settimeout(0.2)  # only wait for 0.2s so network thread is exitable
        sock.bind(('', server_port))
        my_ip = socket.gethostbyname(socket.gethostname())
        
        print("Running multiFlut server at " +
              str(my_ip) + ":" + str(server_port))

        print(get_canvas_size(args.host, args.port))

        threading.Thread(target=network_task, daemon=True).start()
        check_timeout()  # start checking for timeouted clients
        while(running):
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        running = False
        print('Exiting...')
        # print(clients)
        sys.exit()


if __name__ == "__main__":
    main()
