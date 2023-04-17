import json
import socket
import threading

from utils import get_parse

PORT = 11451


def handle(client_sock: socket.socket):
    while True:
        try:
            client_sock.send(b"Input your command, format: ip<space>port<space>number1<space>number2\n"
                             b"eg:1.1.1.1 11111 1 2\n")

            recv = client_sock.recv(4096)

            if len(recv) == 0:
                break

            if len(recv) > 100:
                client_sock.send(b"Error:" + b"Toooooooooo Looooooong!" + b'\n')
                continue

            parse_result, is_error, error_string = get_parse(recv)
            ip, port, num1, num2 = parse_result

            if is_error:
                client_sock.send(b"Error:" + error_string.encode() + b'\n')
                continue
            try:
                assert ip is not None
                assert port is not None
                assert num1 is not None
                assert num2 is not None
            except AssertionError:
                client_sock.send(b"Error:" + b"Input Format Wrong!" + b'\n')
                continue

            if abs(num2) < 1e-5:
                client_sock.send(b"Error: Number 2 is too close to 0" + b'\n')
                continue

            new_sock = socket.socket()
            new_sock.settimeout(2)

            try:
                new_sock.connect((ip, port))
                new_sock.send(recv)
                number = new_sock.recv(4096)
                client_sock.send(b"Result: " + number + b"\n")
            except (TimeoutError, BlockingIOError, socket.error):
                client_sock.send(b"Can't Connect, make sure the server IP and Port is right\n")
            finally:
                new_sock.close()

        except UnicodeEncodeError:
            continue

        except socket.error:
            break

    try:
        client_sock.close()
    except socket.error:
        pass


if __name__ == '__main__':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PORT))
    s.listen()

    while True:
        try:
            ck, c_info = s.accept()
            threading.Thread(target=handle, args=(ck,), name="client").start()
        except KeyboardInterrupt:
            s.close()
