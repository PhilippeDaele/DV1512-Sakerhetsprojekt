#!/bin/bash

for port in {5001..5009};
do
    for i in {1..10}; 
    do
        curl "http://127.0.0.1:$port/set_status?new_status=Active"
    done
done

