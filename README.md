# KAUST_CS231_Project
KAUST_CS231_Project, To build a proxy server

![GitHub Pipenv locked Python version](https://img.shields.io/badge/python-%3E%3D3.7-blue)
![Build Pass Green](https://img.shields.io/badge/build-passed-green)

> Welcome to push issues in Github! 🥰

[toc]

## Assumptions

* The user can only access the Proxy Ports. the configuration file is unknown and untouchable for the user
* For convenience, we only consider proxy has only 1 machine with different ports, the same as backend.
* The configuration file is right, without being corrupted.

## How to Run it
The program will automatically read `config.json` in the same dictory.
### Run it
Run the Proxy
```shell
python proxy.py <--allow_local>
```

Run the Backend
```shell
python proxy.py <--allow_local>
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
* Max QPS is 100 for new user in proxy, for connections that already established, depends on the hardware