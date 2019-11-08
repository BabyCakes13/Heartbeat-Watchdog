#!/bin/bash

CENTRALISED="0"

echo "Startig to create instances..."
ZONE=europe-west1-d

gcloud config set compute/zone $ZONE

for i in {0..5}
do
	echo
#   gcloud compute instances create --zone $ZONE --image-family centos-8 --image-project=centos-cloud centos-test-$i
done
echo "Completed creating instances."
echo "Starting to copy client and server python applications on the instances..."
for i in {0..5} 
do
   gcloud compute ssh centos-test-$i -- mkdir /tmp/heartbeat/
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
   fi
done
echo "Complete."
