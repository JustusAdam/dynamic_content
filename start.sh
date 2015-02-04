#!/bin/bash

BASEDIR=`dirname $0`

cd ${BASEDIR}

PYTHONPATH=. python3 ./demo_app/main.py
