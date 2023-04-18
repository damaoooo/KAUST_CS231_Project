import ipaddress
import os
import argparse


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--ip", type=str, required=True, help="The IP address you want to connect")
    arg_parser.add_argument("-p", "--port", type=int, required=True, help="The port your want to connect")

    args = arg_parser.parse_args()

    try:
        ipaddress.ip_address(args.ip)
    except ValueError:
        print("Not a valid ip address")
        exit(-1)

    try:
        assert 1 <= args.port <= 65535
    except AssertionError:
        print("Not a valid port range (1-65535)")
        exit(-1)

    os.system(f"nc {args.ip} {args.port}")
