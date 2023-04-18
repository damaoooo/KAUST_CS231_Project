import dataclasses
import ipaddress
import json
import socket
from typing import List, Union, Tuple


def ip_parser(ip: str, allow_local: bool = True) -> str:
    try:
        ip_v = ipaddress.ip_address(ip).version
        ip = str(ipaddress.ip_address(ip))
    except ValueError:
        raise ValueError("Not a valid IP address")

    if ip_v != 4:
        raise ValueError("Not support IPv6 yet")

    if ip.startswith('0') \
            or ip in ['255.255.255.255', '0.0.0.0', '224.0.0.0',
                      '224.0.0.1', '224.0.0.2', '224.0.0.9', '224.0.0.11',
                      ] \
            or ip.startswith('240') \
            or ip.startswith('169.254') \
            or ip.endswith('.0') \
            or ip.startswith("100.64") \
            or ip.endswith('255'):
        if allow_local and ip.startswith('127'):
            pass
        else:
            raise ValueError("Malicious IP Address")

    return ip


def port_parser(port: str) -> int:
    try:
        p = int(port, 10)
    except ValueError:
        raise ValueError("invalid port input")

    if p > 65535 or p < 1024:
        raise ValueError("Malicious Port Range")

    return p


def number_parser(n: str) -> Union[int, float]:
    # hex
    number = 0
    if n.startswith('0x') or n.startswith('0X'):
        try:
            number = int(n, 16)
            return number
        except ValueError:
            raise ValueError("invalid HEX number")

    if n.count('.') == 1:
        try:
            number = float(n)
            number = round(number, 5)
            if number % 1 == 0:
                number = int(number)
            return number
        except ValueError:
            raise ValueError("invalid FLOAT number")

    try:
        number = int(n, 10)
        return number
    except ValueError:
        raise ValueError("Invalid INT number")


def parser(s: bytes, allow_local: bool = True) -> Tuple[str, int, Union[float, int], Union[float, int]]:
    try:
        string: str = s.decode()
    except (UnicodeError, UnicodeDecodeError):
        raise ValueError("Invalid input")

    if len(string) > 100:
        raise ValueError("Tooooooooo looooooooooooong!")

    command: List[str] = string.split(' ')
    if len(command) != 4:
        raise ValueError("command format Error!")

    # For IP
    ip: str = ip_parser(command[0], allow_local=allow_local)

    # Check Port
    port: int = port_parser(command[1])

    # Check 2 numbers
    a = number_parser(command[2])
    b = number_parser(command[3])

    return ip, port, a, b


def get_parse(cmd: bytes, allow_local: bool = True) -> Tuple[Tuple[str, int, Union[float, int], Union[float, int]], bool, str]:
    error_string = ""
    error = False
    p_result = (None, None, None, None)
    try:
        p_result = parser(cmd, allow_local)
    except ValueError as e:
        error = True
        error_string = str(e)
    return p_result, error, error_string


def read_configure(config_file: str):
    with open(config_file, 'r') as f:
        content = f.read()
        f.close()
    configuration = json.loads(content)
    proxy_list: List[Machine] = []
    backend_list: List[Machine] = []
    for proxy1 in configuration["proxy"]:
        proxy_list.append(Machine(ip=proxy1['ip'], port=proxy1['port']))

    for backend1 in configuration['backend']:
        backend_list.append(Machine(ip=backend1['ip'], port=backend1['port']))

    return proxy_list, backend_list, configuration["key"]


def close_socket(sock: socket.socket):
    try:
        sock.close()
    except socket.error:
        return


def number_checker(num1, num2):
    is_error = False
    error_string = ""

    # -----------------------------------------------------------
    #           For dividing, check the divisor
    # -----------------------------------------------------------

    if abs(num2) < 1e-5:
        error_string = "Error: Number 2 is too close to 0"
        is_error = True

    # -----------------------------------------------------------
    #           For pow, check the complex
    # -----------------------------------------------------------

    if num1 < 0 and isinstance(num2, float):
        error_string = "Error: Do NOT support the complex number"
        is_error = True

    # -----------------------------------------------------------
    #           For pow, check the 0 as divisor
    # -----------------------------------------------------------

    if num1 == 0 and num2 < 0:
        error_string = "Error: 0 cannot be raised to a negative power"
        is_error = True

    return is_error, error_string


@dataclasses.dataclass()
class Machine:
    ip: str = dataclasses.field(default="127.0.0.1")
    port: int = dataclasses.field(default=11111)
