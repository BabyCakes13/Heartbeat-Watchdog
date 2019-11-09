#!/bin/bash

NUM=5

CENTRALISED=
RING=
ALL_TO_ALL="yabadabadoo"

echo "Startig to create instances..."
ZONE=europe-west1-d

gcloud config set compute/zone $ZONE

for i in $(seq 0 $NUM)
do
	echo
#   gcloud compute instances create --zone $ZONE --image-family centos-8 --image-project=centos-cloud centos-test-$i
    (gcloud compute ssh centos-test-$i -- sudo systemctl stop heartbeat\* ) &
done
echo "Completed creating instances."
echo "Starting to copy client and server python applications on the instances..."
for i in $(seq 0 $NUM)
do
   gcloud compute ssh centos-test-$i -- mkdir -p /tmp/heartbeat/
   gcloud compute scp *.py *.service centos-test-$i:/tmp/heartbeat/
   gcloud compute ssh centos-test-$i -- sudo cp /tmp/heartbeat/*.py /usr/local/bin/
   
   if [ $CENTRALISED ] ; then 
     #prepare client service
     gcloud compute ssh centos-test-$i -- sed -i "s/whatsoever/centos-test-0/g" /tmp/heartbeat/heartbeat_client.service
     gcloud compute ssh centos-test-$i -- sudo cp /tmp/heartbeat/*.service /etc/systemd/system/
     gcloud compute ssh centos-test-$i -- sudo systemctl daemon-reload
     if [ "0" -eq "$i" ]; then
       gcloud compute ssh centos-test-$i -- sudo systemctl restart heartbeat_server.service
     else
       gcloud compute ssh centos-test-$i -- sudo systemctl restart heartbeat_client.service
     fi
   elif [ $RING ]; then
      server=$((($i+1)%6))
      client=$i
      
      gcloud compute ssh centos-test-$client -- sed -i "s/whatsoever/centos-test-$server/g" /tmp/heartbeat/heartbeat_client.service
      gcloud compute ssh centos-test-$client -- sudo cp /tmp/heartbeat/*.service /etc/systemd/system/
      gcloud compute ssh centos-test-$client -- sudo systemctl daemon-reload
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_server.service
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_client.service
      
   elif [ $ALL_TO_ALL ]; then
      servers=`for s in $(seq 0 $NUM) ; do if [ "$s" -eq "$i" ] ; then continue ; fi ; echo -n "centos-test-$s\ " ; done ` 
      client=$i
      
      gcloud compute ssh centos-test-$client -- sed -i "s/whatsoever/$servers/g" /tmp/heartbeat/heartbeat_client.service
      gcloud compute ssh centos-test-$client -- sudo cp /tmp/heartbeat/*.service /etc/systemd/system/
      gcloud compute ssh centos-test-$client -- sudo systemctl daemon-reload
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_server.service
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_client.service
   else 
       echo " Please select a mode of operation"
   fi
   
done
echo "Complete."
