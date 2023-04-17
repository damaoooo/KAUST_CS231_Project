import ipaddress
from typing import List, Union, Tuple


def ip_parser(ip: str) -> str:
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
            or ip == '127.0.0.1' \
            or ip.endswith('255') \
            or ip.startswith('127'):
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
    if n.startswith('0x'):
        try:
            number = int(n, 16)
            return number
        except ValueError:
            raise ValueError("invalid HEX number")

    if n.count('.') == 1:
        try:
            number = float(n)
            number = round(number, 5)
            return number
        except ValueError:
            raise ValueError("invalid FLOAT number")

    try:
        number = int(n, 10)
        return number
    except ValueError:
        raise ValueError("Invalid INT number")


def parser(s: bytes) -> Tuple[str, int, Union[float, int], Union[float, int]]:
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
    ip: str = ip_parser(command[0])

    # Check Port
    port: int = port_parser(command[1])

    # Check 2 numbers
    a = number_parser(command[2])
    b = number_parser(command[3])

    return ip, port, a, b


def get_parse(cmd: bytes) -> Tuple[Tuple[str, int, Union[float, int], Union[float, int]], bool, str]:
    error_string = ""
    error = False
    p_result = (None, None, None, None)
    try:
        p_result = parser(cmd)
    except ValueError as e:
        error = True
        error_string = str(e)
    return p_result, error, error_string