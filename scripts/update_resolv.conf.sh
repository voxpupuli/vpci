#!/bin/bash

server=$1

ssh ubuntu@${server} 'echo nameserver 2620:0:ccc::2 >> /etc/resolv.conf'
