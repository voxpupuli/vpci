# This script is used purely for development

import pprint

pp = pprint.PrettyPrinter(indent=4)


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

org = 'puppetlabs'
name = 'puppetlabs-haproxy'
number = 292

job = job_format
job['org'] = org
job['name'] = name
job['number'] = number
job['slug'] = org + '/' + name
job['jobs'].append('experiments/long_running_fail')
job['jobs'].append('experiments/long_running_success')
job['jobs'].append('experiments/simple_fail')
job['jobs'].append('experiments/simple_success')

pp.pprint(job)
#r.rpush('vpci_job_queue', json.dumps(job))
