#!/bin/bash

IP_ADDRESS="127.0.0.1"
PORT_START=1
PORT_END=10000

success_list=()

for ((port=$PORT_START; port<=$PORT_END; port++)); do
    nc -z -w 1 $IP_ADDRESS $port > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success_list+=($port)
    fi
done

echo "Successful attempts:"
for port in "${success_list[@]}"; do
    echo "Port $port"
done