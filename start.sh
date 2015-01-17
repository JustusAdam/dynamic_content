#!/bin/bash

# TODO add shell functions here that adds 'dyc' to the pythonpath?

BASEDIR=`dirname $0`

cd $BASEDIR

python3 ./dyc/application/main.py --port 9012 --host localhost --runlevel testing --pathmap multitable --server wsgi
