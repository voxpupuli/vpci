#!/bin/bash

sqlite3 job_db.sqlite 'update pull_requests set merge_commit_sha="foo" where name="puppetlabs/puppetlabs-haproxy";'

