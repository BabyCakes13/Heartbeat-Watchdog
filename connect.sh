#!/bin/bash

echo "Startig to create instances..."
ZONE=europe-west1-d
for i in {0..5}
do
   gcloud compute instances create --zone $ZONE --image-family centos-8 --image-project=centos-cloud centos-test-$i
done
echo "Complete."
