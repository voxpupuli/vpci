#!/bin/bash

import time
import pprint
import uuid

import json
import redis
import yaml
import shade
import paramiko

server_name = 'ubuntu 14.04 server'
keypair_name = 'vpci'

job_format = {
    'format_vers': 0.1,
    'org': None,
    'name': None,
    'slug': None,
    'number': None,
    'node': {
        'name': None,
        'flavor': None,
    },
    'environment': {
        'CI_SYSTEM': 'vpci',
    },
    'jobs': [
        'noop',
    ],
}

def build_vm():

    # set env vars and build vm
    image = cloud.get_image(image_name)
    key = cloud.search_keypairs(name_or_id=keypair_name)
    server_name = "vpci-testnode-" + str(uuid.uuid4())
    cloud.create_server(server_name, image['id'], flavor['id'], key_name=key[0]['id'])
    server = cloud.get_server(server_name)

    # poll until the node comes up
    while True:
        print "HODOR, cloud slow"
        time.sleep(2)
        server = cloud.get_server(server_name)
        if len(server.addresses) > 0:
            break


def run_job():
    job = r.lpop('vpci_job_queue')


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    run_job()


