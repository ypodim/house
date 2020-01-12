#!/bin/bash

# rc.local:
# export HOUSE_PATH=/home/pi/ws/house/atlas
# 

export HOUSE_PATH=/home/pi/ws/house/atlas
export HOUSE_LOG="house.log"

if [ -z ${HOUSE_PATH+x} ]; then echo "HOUSE_PATH var is unset, cannot continue" && exit 0; fi
if [ -z ${HOUSE_LOG+x} ];  then echo "HOUSE_LOG var is unset, cannot continue" && exit 0; fi

cd $HOUSE_PATH
python3 main.py --log_file_prefix=$HOUSE_PATH/$HOUSE_LOG