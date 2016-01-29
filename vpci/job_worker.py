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

    return server


def logline(line):
    global all_output
    all_output += line
    all_output += '\n'
    print line


def run_and_print(client, command):
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    logline("command: {0}".format(command))
    logline("stdout: {0}".format(stdout.read().strip()))
    err = stderr.read()
    if err  != "":
        logline("stderr: {0}".format(err))


def create_ssh_client(server):
    # All this is custom for testing
    # TODO fix it up to use shade
    ip = '192.168.122.17'
    #
    # Initialize paramiko for SSH
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username='ubuntu', look_for_keys=False, key_filename=conf['ssh_private_key'])
    return client


def basic_information(client):
    # collect basic node information
    run_and_print(client, 'pwd')
    run_and_print(client, 'hostname')
    run_and_print(client, 'cat /etc/issue')
    run_and_print(client, 'nproc')


def setup_node(client):
    # perform setup tasks
    run_and_print(client, 'rm -fr vpci')
    run_and_print(client, 'git clone git://192.168.122.1/voxpupuli/vpci/.git')
    run_and_print(client, 'ls vpci/jobs')


def run_job():
    #job = r.lpop('vpci_job_queue')
    job = r.lindex('vpci_job_queue', 1)
    if job == None:
        logline("No work to do")
        return
    job = json.loads(job)

    logline("Working on job")
    pp.pprint(job)

    #server = build_vm()
    server = {}
    client = create_ssh_client(server)

    basic_information(client)
    setup_node(client)


if __name__ == "__main__":
    global all_output
    all_output = ""
    pp = pprint.PrettyPrinter(indent=4)

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    run_job()
    #print all_output


