#!/bin/bash

repo="https://github.com/puppetlabs/puppetlabs-apache"
repodir="puppetlabs-apache"
ref=""
pr=1334

VPCI_ROOT=~/vpci
export BEAKER_TESTMODE=local

${VPCI_ROOT}/scripts/allow_local_ssh_root
${VPCI_ROOT}/scripts/clone_repo $repo $ref
${VPCI_ROOT}/scripts/beaker_prepare
cd $repodir

${VPCI_ROOT}/scripts/checkout_pr $pr
cp spec/acceptance/nodesets/default.yml spec/acceptance/nodesets/localssh.yml
${VPCI_ROOT}/scripts/run_beaker_rspec
