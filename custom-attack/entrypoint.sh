#!/bin/sh

echo "nameserver 192.168.100.53" > /etc/resolv.conf
echo "search campus-savona.local" >> /etc/resolv.conf
wait4x tcp "${SCADA_HOST}:${SCADA_PORT}"
echo "Scada Up"
cd src
exec python main.py