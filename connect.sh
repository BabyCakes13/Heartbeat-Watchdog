#!/bin/bash

echo "Startig to create instances..."
for i in {0..5}
do
   gcloud compute instances create --image-family centos-8 --image-project=centos-cloud centos-test-$i
done
echo "Complete."
