#!/bin/bash

repo="https://github.com/puppetlabs/puppetlabs-haproxy"
ref=""

VPCI_ROOT=~/vpci

${VPCI_ROOT}/scripts/allow_local_ssh_root
${VPCI_ROOT}/scripts/clone_repo $repo $ref
cd puppetlabs-haproxy
${VPCI_ROOT}/scripts/write_nodeset
${VPCI_ROOT}/scripts/run_beaker_rspec
