#!/usr/bin/env python

import time
import pprint

import json
import redis
import yaml

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


def process_haproxy(org, name, number):
    job = job_format
    job['org'] = org
    job['name'] = name
    job['number'] = number
    job['slug'] = org + '/' + name
    pp.pprint(job)
    r.rpush('vpci_job_queue', json.dumps(job))

def process_puppet_core(org, name, number):
    return


def pump(pr):
    org, name, number = pr.split('/')
    print org, name, number
    slug = org + '/' + name
    #TODO betterify this
    if slug == 'puppetlabs/puppetlabs-haproxy':
        process_haproxy(org, name, number)
    if slug == 'puppetlabs/puppet':
        process_puppet_core(org, name, number)


def main_loop():
    while True:
        pr = r.lpop('new_pull_requests')
        if pr is None:
            print "looping"
            time.sleep(5)
        else:
            pump(pr)




if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    main_loop()

