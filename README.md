# Vox Pupuli CI

This is the second generation CI system for VoxPupuli. The first system, pcci, became unmanagable so it was decided to build out this system with the best ideas of the first but more flexibility and maturity in the coding practices and architecture.


## Architecture

* VPCI will store historical build information in a database, allowing unique build-ids for every build

* VPCI will store git repo information in a database.

* VPCI will use redis as a durable queue for jobs.

* VPCI will use OpenStack nova for test builders.

* VPCI will be made up of several smaller daemons that will be controlled by a userspace process manager.


