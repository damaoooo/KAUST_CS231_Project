import socket
import unittest
from utils import *
from proxy import *


class TestParser(unittest.TestCase):
    def test_ip(self):
        with self.assertRaises(ValueError):
            ip_parser('1.0.0.0')
        # with self.assertRaises(ValueError):
        #     ip_parser('127.0.0.1')
        with self.assertRaises(ValueError):
            ip_parser("fe80::9901:f43c:d50d:249d")
        with self.assertRaises(ValueError):
            ip_parser('123jdslj91jorqwflkjds1943jrel')
        with self.assertRaises(ValueError):
            ip_parser('255.256.0.1')
        # self.assertEqual('127.0.0.2', ip_parser('127.0.0.2'))

    def test_port(self):
        self.assertEqual(port_parser('12345'), 12345)
        with self.assertRaises(ValueError):
            port_parser('114514')
        with self.assertRaises(ValueError):
            port_parser('-1')
        with self.assertRaises(ValueError):
            port_parser('0x123')
        with self.assertRaises(ValueError):
            port_parser('0')
        with self.assertRaises(ValueError):
            port_parser('1000.0')
        with self.assertRaises(ValueError):
            port_parser('1111.1')
        with self.assertRaises(ValueError):
            port_parser('1.1.1.1')

    def test_number(self):
        self.assertEqual(number_parser('114514'), 114514)
        self.assertEqual(number_parser('0x114514'), 0x114514)
        self.assertTrue(abs(number_parser('-0.0000000000000000001') - 0) < 1e-4)
        self.assertEqual(number_parser('-5.3'), -5.3)
        with self.assertRaises(ValueError):
            number_parser('0x123.123')
        with self.assertRaises(ValueError):
            number_parser('.0x1')
        with self.assertRaises(ValueError):
            number_parser('0xbBDG')
        with self.assertRaises(ValueError):
            number_parser('1e-3')
        self.assertEqual(number_parser('-2'), -2)
        self.assertEqual(number_parser('-2.32'), -2.32)

    def test_parser(self):
        self.assertEqual(parser(b'1.2.3.4 1234 1 2'), ('1.2.3.4', 1234, 1, 2))
        self.assertEqual(parser(b'1.2.3.4\x201234 1.12 2.34'), ('1.2.3.4', 1234, 1.12, 2.34))
        with self.assertRaises(ValueError):
            parser(b'\x12\x32\x202345 -0.0000000000000123123 000000000000000000000.10000000000')
        with self.assertRaises(ValueError):
            parser(b'\x55.1. ')
        with self.assertRaises(ValueError):
            parser(b'1.1.1.1. 1. 1 1')
        with self.assertRaises(ValueError):
            parser(b'1.1.1.1 11111. 1 1')


class TestProxy(unittest.TestCase):
    def setUp(self):
        self.backend_server = [
            Machine(ip="11.4.5.14", port=11451),
            Machine(ip="1.1.1.1", port=45454)
        ]
        self.proxy = Proxy(44442, conf_backend_list=self.backend_server, conf_key="114")

    def test_commander(self):
        helper = self.proxy.get_helper()
        for backend in self.backend_server:
            self.assertIn(f"{backend.ip}:{backend.port}", helper)


if __name__ == '__main__':
    # unittest.main()
    t = TestProxy()
    t.test_commander()
