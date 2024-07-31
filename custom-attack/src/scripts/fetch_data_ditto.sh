#!/bin/sh
curl -s administrator:{{password_ditto}}@{ip_ditto}/api/2/search/things | curl -X POST -H 'Content-Type: application/json' -d @- {this_ip}/data_ditto