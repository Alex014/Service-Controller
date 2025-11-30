#!/bin/bash
FILE="/home/privateness/.update"  

while :
do
    if [ -f $FILE ]; then
        systemctl stop controller && \
        cd /home/privateness/Service-Controller && \
        git pull origin master && \
        systemctl start controller && \
        rm $FILE
    fi

    sleep 1
done
