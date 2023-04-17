import socket
import threading

from utils import get_parse

IP = "10.72.138.84"
PORT = 11452

CDN_IP = "10.72.138.86"
CDN_PORT = 11451


def handle(client_socket: socket.socket, client_info: tuple):
    while True:
        recv = client_socket.recv(4096)
        if len(recv) == 0:
            break

        if len(recv) > 100:
            break
        print(client_info, recv)
        res, error, error_info = get_parse(recv)
        if error:
            print("parse wrong")
            break

        ip, port, num1, num2 = res
        if ip != IP or port != PORT:
            print(client_info, ip, port, "not me")
            break

        if abs(num2) < 1e-5:
            print("number 2 too small")
            break

        # All OK
        result = num1 / num2
        result = round(result, 3)
        client_socket.send(str(result).encode())
        break
    client_socket.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PORT))
    s.listen()
    while True:
        try:
            client_sock, client_infos = s.accept()
            print(client_infos)
            if client_infos[0] != CDN_IP:
                client_sock.close()
                continue
            threading.Thread(target=handle, args=(client_sock, client_infos)).start()
        except KeyboardInterrupt:
            s.close()



