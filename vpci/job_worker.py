#!/bin/bash

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

def run_job():
    job = r.lpop('vpci_job_queue')


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    run_job()


