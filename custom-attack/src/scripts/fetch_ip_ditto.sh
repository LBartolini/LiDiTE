#!/bin/sh
getent hosts frontend | awk '{{ print $1 }}' | curl -X POST -H 'Content-Type: text/plain' -d @- {this_ip}/ip_ditto