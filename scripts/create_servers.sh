#!/bin/bash


for i in {0..3}
do
        nova boot --image 'ubuntu 14.04 server'  --flavor small --key vpci vpci-testnode-${i}
done

