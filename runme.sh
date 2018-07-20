#!/bin/bash

export FLASK_APP=main.py
if [ $# -eq 1 ]
then
        flask run --host=$1
else
        flask run
fi
