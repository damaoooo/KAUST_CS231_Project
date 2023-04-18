import logging
import socket
import json
import time
from typing import List
import threading

from utils import Machine, close_socket, read_configure

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)


class Backend:
    def __init__(self, port: int, conf_proxy_list: List[Machine], conf_key: str):
        self.proxy_list = conf_proxy_list
        self.port = port
        self.key = conf_key
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.die = False

    def __del__(self):
        close_socket(self.socket)

    def start(self):
        try:
            self.socket.bind(('0.0.0.0', self.port))
        except socket.error:
            print(f"Port Bind Error, Port is {self.port}")
            return
        self.socket.settimeout(0.5)
        self.socket.listen()
        while True:
            try:
                client_sock, client_info = self.socket.accept()
                logging.info(f"[+] user {client_info} Connected")
                threading.Thread(target=self.handle, args=(client_sock, client_info)).start()

            except TimeoutError:
                if self.die:
                    return

            except KeyboardInterrupt:
                return

    def handle(self, client_socket: socket.socket, client_info: tuple):
        client_ip, client_port = client_info

        # -----------------------------------------------------------
        #           Don't talk to strange people
        # -----------------------------------------------------------
        is_valid_proxy = False

        for proxy_ in self.proxy_list:
            if client_ip == proxy_.ip:
                is_valid_proxy = True
                break

        if not is_valid_proxy:
            close_socket(client_socket)
            logging.log(level=logging.INFO, msg=f"[+] Invalid Proxy From {client_info}")
            return

        # -----------------------------------------------------------
        #           Check the validation of JSON
        # -----------------------------------------------------------
        recv = client_socket.recv(4096)

        if len(recv) == 0 or len(recv) > 200:
            close_socket(client_socket)
            return

        try:
            content = json.loads(recv)
        except json.decoder.JSONDecodeError:
            # No NEED to log the bad content
            logging.log(level=logging.INFO, msg=f"[+] Invalid JSON From {recv}")
            close_socket(client_socket)
            return

        # -----------------------------------------------------------
        #           Check the key and content
        # -----------------------------------------------------------
        try:
            recv_key = content['key']
            num1 = content['num1']
            num2 = content['num2']
            assert recv_key == self.key
        except (KeyError, AssertionError):
            logging.info(f"malformed payload {content}")
            close_socket(client_socket)
            return

        # Assumptions:
        # 1. num2 != 0 2. No Complex Number
        try:
            assert num2 != 0
            assert not (num1 < 0 and isinstance(num2, float))
            assert not (num1 == 0 and num2 < 0)
        except AssertionError:
            logging.info(f"Not Correct INPUT NUM1:{num1}, NUM2: {num2}")
            close_socket(client_socket)
            return

        result1 = num1 / num2
        result1 = round(result1, 5)

        if isinstance(num1, int) and isinstance(num2, int):
            result2 = pow(num1, num2, 0xFFFFFFFF)
        else:
            try:
                result2 = round(pow(num1, num2), 5)
            except OverflowError:
                result2 = "Overflow, The result is Too Large"

        ret = f"res1: {result1}, res2: {result2}"
        client_socket.send(ret.encode())
        time.sleep(0.1)
        close_socket(client_socket)


if __name__ == '__main__':

    proxy_list, backend_list, key = read_configure("config.cfg")
    backend_instances = []
    for backend_ in backend_list:
        b = Backend(port=backend_.port, conf_proxy_list=proxy_list, conf_key=key)
        threading.Thread(target=b.start).start()
        backend_instances.append(b)

    while True:
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            for b in backend_instances:
                b.die = True
            break
