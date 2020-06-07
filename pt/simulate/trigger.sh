#!/bin/bash
BASEDIR=$(dirname "$0")
cd $BASEDIR/../../
/usr/local/bin/pipenv run python3 -m pt.simulate.main -b $1 -p $2 >> /tmp/$1.log 2>&1
