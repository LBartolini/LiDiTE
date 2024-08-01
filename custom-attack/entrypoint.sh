#!/bin/sh

wait4x tcp "${SCADA_HOST}:${SCADA_PORT}"
echo "Scada Up"
cd src
exec python main.py