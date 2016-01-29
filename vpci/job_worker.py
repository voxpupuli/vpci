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


class Remote():

    def __init__(self, client, environment_hash):
        self.client = client
        self.environment_hash = environment_hash
        self.all_output = ""
        env_header = "export"
        for k,v in self.environment_hash.iteritems():
            env_header +=" {0}={1}".format(k,v)
        env_header += "; "
        self.environment_string = env_header
        print "Running all commands with enviroment:"
        print self.environment_string


    def run_and_print(self, command):
        cmd = self.environment_string + command
        stdin, stdout, stderr = self.client.exec_command(cmd)
        self.logline("command: {0}".format(command))
        self.logline("stdout: {0}".format(stdout.read().strip()))
        err = stderr.read()
        if err  != "":
            self.logline("stderr: {0}".format(err))


    def logline(self, line):
        self.all_output += line
        self.all_output += '\n'
        print line


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


def basic_information(remote):
    # collect basic node information
    remote.run_and_print('pwd')
    remote.run_and_print('hostname')
    remote.run_and_print('cat /etc/issue')
    remote.run_and_print('nproc')
    remote.run_and_print("env")
    remote.run_and_print("echo $CI_SYSTEM")


def local_setup_node(remote):
    # perform setup tasks
    remote.run_and_print('rm -fr vpci')
    remote.run_and_print('git clone git://192.168.122.1/voxpupuli/vpci/.git')
    remote.run_and_print('ls vpci/jobs | wc -l')


def run_job():
    #job = r.lpop('vpci_job_queue')
    job = r.lindex('vpci_job_queue', 1)
    if job == None:
        print "No work to do"
        return
    job = json.loads(job)

    print "Working on job"
    pp.pprint(job)

    #server = build_vm()
    server = {}
    client = create_ssh_client(server)


    remote = Remote(client, job['environment'])

    basic_information(remote)
    local_setup_node(remote)

    print "This test will run the following jobs: "
    for job_script in job['jobs']:
        print job_script,
    print
    print

    for job_script in job['jobs']:
        print "Running Job", job_script
        remote.run_and_print("./vpci/jobs/{0}".format(job_script))
    print


if __name__ == "__main__":
    all_output = ""
    pp = pprint.PrettyPrinter(indent=4)

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    run_job()
    #print all_output


