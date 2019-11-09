#!/bin/bash

NUM=5

CENTRALISED=
RING=
ALL_TO_ALL="yabadabadoo"

ZONE=europe-west1-d

gcloud config set compute/zone $ZONE # setup default zone so we are not asked all the time

# create the necessary instances based on the NUM parameter, and stop all the heartbeat services which are turned on on the machines
for i in $(seq 0 $NUM)
do
	echo
    gcloud compute instances create --zone $ZONE --image-family centos-8 --image-project=centos-cloud centos-test-$i
    gcloud compute ssh centos-test-$i -- sudo systemctl stop heartbeat\*
done

for i in $(seq 0 $NUM)
do
   # deploy the python server and client scripts
   gcloud compute ssh centos-test-$i -- mkdir -p /tmp/heartbeat/ # create a heartbeat/ directory in tmp, since sudo is not required for that
   gcloud compute scp *.py *.service centos-test-$i:/tmp/heartbeat/ # copy the files (client and server)
   gcloud compute ssh centos-test-$i -- sudo cp /tmp/heartbeat/*.py /usr/local/bin/ # move the files to the desired location without having to use sudo
   
   # CENTRALISED HEARTBEAT
   if [ $CENTRALISED ] ; then 
     # setup the necesary files in the right directories
     gcloud compute ssh centos-test-$i -- sed -i "s/whatsoever/centos-test-0/g" /tmp/heartbeat/heartbeat_client.service # prepare the client service by setting up the necessary server
     gcloud compute ssh centos-test-$i -- sudo cp /tmp/heartbeat/*.service /etc/systemd/system/ # move the services from temp to systemd location
     gcloud compute ssh centos-test-$i -- sudo systemctl daemon-reload # reload system files in systemd
     
     if [ "0" -eq "$i" ]; then # for centralised, always chose the server to always be the 0th centos instance
       gcloud compute ssh centos-test-$i -- sudo systemctl restart heartbeat_server.service
     else
       gcloud compute ssh centos-test-$i -- sudo systemctl restart heartbeat_client.service # the others are just clients
     fi
     
   # RING HEARTBEAT
   elif [ $RING ]; then
      server=$((($i+1)%6)) # the server for each instance will be the next instance (for 0, 5)
      client=$i
      
      gcloud compute ssh centos-test-$client -- sed -i "s/whatsoever/centos-test-$server/g" /tmp/heartbeat/heartbeat_client.service # setup the client service with the actual server name
      gcloud compute ssh centos-test-$client -- sudo cp /tmp/heartbeat/*.service /etc/systemd/system/ # move the services to systemd location to systemd
      gcloud compute ssh centos-test-$client -- sudo systemctl daemon-reload # reload the system files in systemd
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_server.service # restart the services so the changes are made
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_client.service
      
   # ALL_TO_ALL HEARTBEAT
   elif [ $ALL_TO_ALL ]; then
      # create a list of all server names before waiting for them to be initialised, so all of them (except the current number) will be servers and passed to the client service (which needs to know what to connect to)
      servers=`for s in $(seq 0 $NUM) ; do if [ "$s" -eq "$i" ] ; then continue ; fi ; echo -n "centos-test-$s\ " ; done ` 
      client=$i
      
      gcloud compute ssh centos-test-$client -- sed -i "s/whatsoever/$servers/g" /tmp/heartbeat/heartbeat_client.service # pass all the servers except the current number
      gcloud compute ssh centos-test-$client -- sudo cp /tmp/heartbeat/*.service /etc/systemd/system/ # from here same old same old
      gcloud compute ssh centos-test-$client -- sudo systemctl daemon-reload
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_server.service
      gcloud compute ssh centos-test-$client -- sudo systemctl restart heartbeat_client.service
      
   else 
       echo " Please select a mode of operation"
   fi 
done
