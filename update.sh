#!/bin/bash
FILE="/home/privateness/.update"  

while :
do
    if [ -f $FILE ]; then
        cd /home/privateness/Service-Controller && \
        cp update.sh ~/update.sh && \
        git pull origin master && \
        rm $FILE && \
        systemctl start controller
    fi

    sleep 1
done
