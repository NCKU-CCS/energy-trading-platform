#!/bin/bash
#! -a: account
#! -p: password 
#! -s: start_time
#! -e: end_time
#! -v: bidding value
#! -m: bidding price
#! -t: bidding type
BASEDIR=$(dirname "$0")
START=$(date +"%Y/%m/%d ")00
END=$(date +"%Y/%m/%d " --date="+1 days")00
cd $BASEDIR/../../../
/usr/local/bin/pipenv run python3 -m pt.simulate.data -a $1 -p $2 -s $3 -e $4 -v $5 -m $6 -t $7 >> /tmp/bidsubmit-$1.log 2>&1
