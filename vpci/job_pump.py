#!/usr/bin/env python

import time

import redis
import yaml

def pump(pr):
    org, name, number = pr.split('/')
    print org, name, number
    slug = org + '/' + name
    #TODO betterify this
    if slug == 'puppetlabs/puppetlabs-haproxy':
        process_haproxy()
    if slug == 'puppetlabs/puppet':
        process_puppet_core()


def main_loop():
    while True:
        new_pr = r.lindex('new_pull_requests', 0)
        if new_pr is None:
            print "looping"
            time.sleep(5)
        else:
            pump(new_pr)




if __name__ == "__main__":

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    main_loop()

