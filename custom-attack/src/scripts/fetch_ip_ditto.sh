#!/bin/sh
getent hosts frontend | awk '{ print $1 }' | curl -X POST -H 'Content-Type: text/plain' -d @- %s:%s/ip_ditto