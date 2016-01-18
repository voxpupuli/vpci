#!/bin/bash

repo="https://github.com/puppetlabs/puppetlabs-apache"
repodir="puppetlabs-apache"
ref=""
pr=1334

VPCI_ROOT=~/vpci
export BEAKER_TESTMODE=local

${VPCI_ROOT}/scripts/allow_local_ssh_root
${VPCI_ROOT}/scripts/clone_repo $repo $ref
cd $repodir

${VPCI_ROOT}/scripts/checkout_pr $pr
${VPCI_ROOT}/scripts/write_nodeset
${VPCI_ROOT}/scripts/run_beaker_rspec
