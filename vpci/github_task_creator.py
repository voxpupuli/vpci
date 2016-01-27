#!/usr/bin/env python

from datetime import datetime
import time

from github import Github, UnknownObjectException
import json
import redis
import sqlite3
import yaml


def init_db_or_pass(conn):
    """
    Attempt to validate if the database is set up, else create one
    """
    c = conn.cursor()

    #c.execute('''CREATE TABLE stocks
    #                     (date text, trans text, symbol text, qty real, price real)''')

    # Insert a row of data
    #c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

    # Save (commit) the changes
    try:
        c.execute("SELECT * FROM pull_requests LIMIT 1")
        for row in c.execute("SELECT * FROM pull_requests"):
            print row
        return
    except sqlite3.OperationalError:
        c.execute('''CREATE TABLE pull_requests
                             (id INTEGER PRIMARY KEY ASC, name text, number integer, merge_commit_sha text)''')

    conn.commit()


def totimestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt - epoch
    # return td.total_seconds()
    return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 )


def scan_and_update(repos, db):

    for repo in repos:
        #r.sadd('repos', str(repo)) #TODO reflect in DB maybe
        pulls = g.get_repo(repo).get_pulls()
        print "repo is: {0}".format(repo)
        print "pulls are: ",
        for p in pulls:
            print p.number,

        for pull in pulls:
            number = pull.number
            name = repo
            # from pdb import set_trace; set_trace()
            unique_name = repo + "/" + str(number)

            current_merge_commit_sha = pull.merge_commit_sha
            if current_merge_commit_sha is None:
                current_merge_commit_sha = ""
            cursor = db.cursor()
            current = cursor.execute("SELECT * FROM pull_requests WHERE name=? and number =?", (name, number)).fetchall()

            if current == []:
                print "Discovered new pull request, adding"
                cursor.execute('INSERT INTO pull_requests values (NULL,?,?,?)', (name, number, current_merge_commit_sha))
                db.commit()



def derp():
    merge_commit_sha = stored_pull['merge_commit_sha']
    print unique_name
    print merge_commit_sha
    print current_merge_commit_sha
    if merge_commit_sha != current_merge_commit_sha:
        stored_pull['merge_commit_sha'] = current_merge_commit_sha
        job = {}
        job['unique_name'] = unique_name

        try:
          pcci_file = yaml.load(g.get_repo(repo).get_contents('.pcci.yml'))
          os_sets = []
          os_sets.append(pcci_file['nodesets'])
        except UnknownObjectException,e:
          os_sets = ['trusty','centos7']

        for os_set in os_sets:
            job['nodeset'] = os_set
            r.rpush('todo', json.dumps(job))

    r.set(unique_name, json.dumps(stored_pull))


if __name__ == "__main__":

    with open('config.yaml') as f:
        conf = yaml.load(f.read())
    f.closed

    github_token = conf['github_auth_token']
    db_file = conf['db_file']

    g = Github(github_token)
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Setup Database

    conn = sqlite3.connect(db_file)
    init_db_or_pass(conn)

    scan_and_update(conf['repos'], conn)
