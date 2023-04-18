# KAUST_CS231_Project
KAUST_CS231_Project, To build a proxy server

![GitHub Pipenv locked Python version](https://img.shields.io/badge/python-%3E%3D3.7-blue)
![Build Pass Green](https://img.shields.io/badge/build-passed-green)

> Welcome to push issues in GitHub! 🥰

## TOC

- [Assumptions](#assumptions)
- [How to Run it](#how-to-run-it)
- [Functionality](#functionality)
- [Avoid Being Attacked](#avoid-being-attacked)


## Assumptions

* The user can only access the Proxy Ports. the configuration file is unknown and untouchable for the user
* For convenience, we only consider proxies are running on only 1 machine but with different ports, the same as backend.
* The configuration file is right, without being corrupted. Because it's invisible to users.

## How to Run it

### Download
```shell
git clone https://github.com/damaoooo/KAUST_CS231_Project
cd KAUST_CS231_Project
```

The program will automatically read `config.json` in the same directory.
### Run it
Run the Proxy
```shell
python proxy.py <--allow_local>
```
`--allow_local` means whether you allow the traffic from `127.0.0.1` . By default, it's true. 
if not very interested in it, you don't need to provide it to the program.

Run the Backend
```shell
python proxy.py
```

### Configuration File
```json
{
  "proxy": [
    {"ip":  "127.0.0.1", "port":  11451},
    {"ip":  "127.0.0.1", "port":  11452}
  ],
  "backend": [
    {"ip": "127.0.0.1", "port":  11453},
    {"ip": "127.0.0.1", "port":  11454}
  ],
  "key": "123456"
}
```
You can modify to meet your requirement. Just follow the sample format.

### Client
just use the native client.
```shell
nc <ip> <port>
e.g.
nc 127.0.0.1 11451
```
For test, you can use the python file in the `client_for_test` directory, but it is the same functionality as nc.
```shell
python client_for_test/bad_client_LI.py --ip 127.0.0.1 --port 11451
```
## Functionality

```                                        
                 +---------+     +----------+  
                 |  proxy1 |     | backend1 |  
                 +---------+     +----------+  
+--------+                                     
|  user  |                                     
+--------+       +---------+     +----------+  
                 |  proxy2 |     | backend2 |  
                 +---------+     +----------+                                

```
User can contact to Proxy 1-n, then ask the Proxy to forward the request to Backend 1-n. Then the result will be returned to the user.
### Input
```
IP Port Num1 Num2
1.1.1.1 5050 1 2
```
* the length of input must be smaller than 100
* Num can be HEX, like 0x1234abcd, can be FLOAT, like 1.23, can be INT, like 123
* FLOAT will be `round(num, 5)`, so 0.000001 will be INT 0
* Don't support Complex Number

### Output
```
Res1 Res2
```

* Res1 is `Num1 / Num2`, the result will round to 5 digits.
* If Num1 and Num2 are integers, then the result will be `(Num1 ^ Num2) % 0xffffffff`, if 
  one of Num1 or Num2 is float number, Res2 is `Num1 ^ Num2`. Then, the result will directly output

## Avoid being Attacked
* SYN Flood. Open the Syn Cookie(Linux) `sysctl -w net.ipv4.tcp_syncookies=1`
* Max QPS is 100 for new user in proxy. For connections that already established, it depends on the hardware

## Directory structure

```
├── README.md
├── backend.py
├── client_for_test
│   ├── bad_client_LI.py
│   └── good_client_LI.py
├── config.cfg
├── proxy.py
├── test_all.py
└── utils.py

```