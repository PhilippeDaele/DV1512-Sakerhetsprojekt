#!/bin/bash

for port in {5001..5009};
do
    python3 pyflooder.py 127.0.0.1 $port 25
done

