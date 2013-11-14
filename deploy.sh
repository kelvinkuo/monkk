#!/bin/bash

HOSTS="root@192.241.207.26 root@106.186.116.170 root@14.18.206.3 root@110.34.240.58 root@70.39.189.80 root@115.85.18.96"
#42.121.76.137 liyxrl(@WAI
for ip in $HOSTS; do
    echo $ip
    scp run_monclient.sh $ip:/root/monkk/run_monclient.sh
    ssh $ip "cd monkk;./kill_monclient.sh;rm *.log;./run_monclient.sh"
    #ssh $ip "rm -rf monkk"
done
