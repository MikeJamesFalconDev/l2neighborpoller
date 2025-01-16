#!/bin/bash

RUNNING_DIR=`dirname $0`
cd $RUNNING_DIR
VENV=$RUNNING_DIR/.venv

if [ ! -d $VENV ];then
	python -m venv $VENV
	source $VENV/bin/activate
	pip install -r ./requirements.txt
else
	source $VENV/bin/activate
fi

python $RUNNING_DIR/src/l2np.py
