# Utility to boot an openstack node
# ssh in, configure
# run some tests
# report on status

import datetime
import pprint
import tempfile
import time
import uuid

import json
import redis
import yaml
import shade
import paramiko

image_name = 'ubuntu 14.04 server'
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
    shade.simple_logging(debug=False)
    cloud = shade.openstack_cloud(name='yolocloud')
    image = cloud.get_image(image_name)
    key = cloud.search_keypairs(name_or_id=keypair_name)
    flavor = cloud.get_flavor_by_ram(1000)
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

    print "server created, sleeping 2 minutes for it to boot"
    time.sleep(120)
    return server


def delete_vm(server):
    print "Deleting server {0}".format(server.name)
    shade.simple_logging(debug=True)
    cloud = shade.openstack_cloud(name='yolocloud')
    cloud.delete_server(server.name)


class Remote():

    def __init__(self, client, environment_hash, timeout=30):
        self.client = client
        self.environment_hash = environment_hash
        self.all_output = ""
        self.timeout = timeout
        env_header = "export"
        for k, v in self.environment_hash.iteritems():
            env_header += " {0}={1}".format(k, v)
        env_header += "; "
        self.environment_string = env_header
        print "Running all commands with enviroment:"
        print self.environment_string

    def run_and_print(self, command):
        cmd = self.environment_string + command
        self.logline("command: {0}".format(command))
        start = datetime.datetime.now()
        stdin, stdout, stderr = self.client.exec_command(cmd)
        stop = datetime.datetime.now()
        if (stop - start) > datetime.timedelta(seconds=10):
            self.logline("execution took {0}".format(stop - start))

        out = stdout.read().strip()
        self.logline("stdout: {0}".format(out.strip()))
        err = stderr.read()
        if err != "":
            self.logline("stderr: {0}".format(err))
            return out, err
        return out, err

    def test_job(self, job_name):
        out, err = self.run_and_print("./vpci/jobs/{0}".format(job_name))
        if out[-4:] == 'FAIL':
            return False
        if out[-4:] == 'PASS':
            return True
        else:
            print "Output undetected: {0}".format(out[-4:])

    def logline(self, line):
        self.all_output += line
        self.all_output += '\n'
        if len(line) > 2000:
            tempdir = tempfile.mkdtemp()
            path = tempdir + '/' + 'output.log'
            with open(path, 'w') as f:
                f.write(line)
            print "Wrote output to {0}".format(path)
        else:
            print line


def create_ssh_client(server):
    if server.addresses['external'][0]['version'] == 6:
        ip = server.addresses['external'][0]['addr']
    else:
        ip = server.addresses['external'][1]['addr']
    #
    # Initialize paramiko for SSH
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    tries = 0
    while tries <= 5:
        try:
            client.connect(ip, username='ubuntu', look_for_keys=False, key_filename=conf['ssh_private_key'])
            return client
        except:
            print "Failed to connect, sleeping for sixty seconds"
            time.sleep(60)
            tries -= 1
    raise paramiko.ssh_exception.NoValidConnectionsError


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
    remote.run_and_print('sudo apt-get update; sudo apt-get install -y git')
    remote.run_and_print('git clone https://github.com/voxpupuli/vpci')
    remote.run_and_print('ls vpci/jobs | wc -l')


def run_job():
    #job = r.lpop('vpci_job_queue')
    job = r.lindex('vpci_job_queue', 0)
    if job == None:
        print "No work to do"
        return
    job = json.loads(job)

    print "Working on job"
    pp.pprint(job)

    server = build_vm()
    #server = {}
    client = create_ssh_client(server)

    remote = Remote(client, job['environment'])

    basic_information(remote)
    local_setup_node(remote)

    results_hash = {}
    print "This test will run the following jobs: "
    for job_script in job['jobs']:
        print job_script,
        results_hash[job_script] = ""
    print
    print

    for job_script in job['jobs']:
        print "Running Job", job_script
        success = remote.test_job(job_script)
        results_hash[job_script] = success
    print

    pp.pprint(results_hash)
    delete_vm(server)

if __name__ == "__main__":
    all_output = ""
    pp = pprint.PrettyPrinter(indent=4)

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    run_job()
    #print all_output


