import json
import select
import socket
import logging
import threading
import time
from typing import List
from utils import get_parse, Machine, read_configure, close_socket, number_checker
import argparse

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)


class Proxy:
    def __init__(self, port: int, conf_backend_list: List[Machine], conf_key: str, conf_allow_local: bool = False):
        self.port = port
        self.key = conf_key
        self.allow_local = conf_allow_local
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.backend_list = conf_backend_list
        self.die = False

    def __del__(self):
        close_socket(self.server_socket)

    def start(self):

        try:
            self.server_socket.bind(('0.0.0.0', self.port))
        except socket.error as e:
            logging.log(level=logging.ERROR, msg=f"Can't Start as Port {self.port}, err: {str(e)}")

        self.server_socket.listen()

        while True:
            rw, _, _ = select.select([self.server_socket], [], [], 0.01)
            if rw:
                c_ck, c_info = self.server_socket.accept()
                logging.log(level=logging.INFO, msg=f"[+] {c_info} connected!")
                threading.Thread(target=self.handle, args=(c_ck,)).start()
            if self.die:
                close_socket(self.server_socket)
                break

    def get_helper(self):
        helper = "\n" + "-" * 50 + "\n"
        helper += f"Hello, Your are in Port: {self.port}\n"
        helper += f"Input your command, format: ip<Space>port<Space>number1<Space>number2<Enter>\n"
        helper += f"eg:1.1.1.1 11111 1 2\n"
        helper += "You can input number as HEX: 0x1234abcd, or INT: 123 or FLOAT 0.1234\n"
        helper += "the FLOAT will be ROUND 5," \
                  " 1.0 will be considered as 1, 0.000001 will be considered as 0"
        helper += f" Available Backend List:\n"

        for backend in self.backend_list:
            helper += f"\n [+] {backend.ip}:{backend.port}"
        helper += "\n"
        helper += "-" * 50 + "\n"

        return helper

    def handle(self, client_sock: socket.socket):

        helper = self.get_helper()

        while True:
            try:
                client_sock.send(helper.encode())

                recv = client_sock.recv(4096)

                if len(recv) == 0:
                    break

                # -----------------------------------------------------------
                #        Check the input length, avoid the overflow
                # -----------------------------------------------------------

                if len(recv) > 100:
                    client_sock.send(b"Error:" + b"Toooooooooo Looooooong!" + b'\n')
                    continue

                # -----------------------------------------------------------
                #                  Check the input format
                # -----------------------------------------------------------

                parse_result, is_error, error_string = get_parse(recv, self.allow_local)
                ip, port, num1, num2 = parse_result

                if is_error:
                    client_sock.send(b"Error:" + error_string.encode() + b'\n')
                    continue

                # -----------------------------------------------------------
                #  Check the input backend address, don't go to weird place
                # -----------------------------------------------------------

                is_valid_backend = False

                for backend in self.backend_list:
                    if backend.ip == ip and backend.port == port:
                        is_valid_backend = True
                        break

                if not is_valid_backend:
                    client_sock.send(b"Error: Make sure your backend is in the list!\n")
                    continue

                # -----------------------------------------------------------
                #           Double check the empty input
                # -----------------------------------------------------------

                try:
                    assert ip is not None
                    assert port is not None
                    assert num1 is not None
                    assert num2 is not None
                except AssertionError:
                    client_sock.send(b"Error:" + b"Input Format Wrong!" + b'\n')
                    continue

                is_error, error_string = number_checker(num1, num2)
                if is_error:
                    client_sock.send(error_string.encode())
                    continue

                new_sock = socket.socket()
                # Avoid the timeout
                new_sock.settimeout(120)

                # -----------------------------------------------------------
                #           For backend network situation
                # -----------------------------------------------------------

                try:
                    new_sock.connect((ip, port))
                    payload = json.dumps({"num1": num1, "num2": num2, "key": self.key})
                    new_sock.send(payload.encode())
                    number = new_sock.recv(4096)
                    client_sock.send(b">>> Result: " + number + b"\n")
                except (TimeoutError, BlockingIOError, socket.error):
                    client_sock.send(b"Can't Connect, make sure the server IP and Port is right\n")
                finally:
                    close_socket(new_sock)

            except UnicodeEncodeError:
                continue

            except socket.error:
                break

        close_socket(client_sock)


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--allow_local", "-l", default=True, type=bool,
                            help="Allow 127.0.0.1 as the proxy and backend")
    args = arg_parser.parse_args()
    allow_local = args.allow_local

    proxy_list, backend_list, key = read_configure("./config.json")
    proxy_instances = []
    for proxy_ in proxy_list:
        p = Proxy(port=proxy_.port, conf_backend_list=backend_list, conf_key=key, conf_allow_local=allow_local)
        threading.Thread(target=p.start).start()
        proxy_instances.append(p)

    while True:
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            for p in proxy_instances:
                p.die = True
            break
