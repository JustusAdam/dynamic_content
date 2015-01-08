#!/bin/bash

# TODO add shell functions here that adds 'dyc' to the pythonpath?

python3 ./dyc/application/main.py --port 9012 --host localhost --runlevel testing --pathmap multitable
