#!/bin/bash

IP_ADDRESS="127.0.0.1"

for port in {5001..5009};
do
    curl "http://$IP_ADDRESS:$port/reset-rate-limit"
done