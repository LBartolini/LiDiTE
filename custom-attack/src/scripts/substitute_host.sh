#!/bin/sh
cp /etc/hosts /etc/hosts.bak
echo "{this_ip}    frontend" >> /etc/hosts