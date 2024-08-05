#!/bin/sh
curl -s administrator:{{password_ditto}}@{ip_ditto}/api/2/things/FDT:gas-generator-1/features | curl -X POST -H 'Content-Type: application/json' -d @- {this_ip}/turbine_ditto