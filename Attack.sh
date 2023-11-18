#!/bin/bash

IP_ADDRESS="127.0.0.1"
PORT_START=1
PORT_END=10000




for port in {5001..5009};
do
    curl "http://$IP_ADDRESS:$port/set_status?new_status=Active"
done