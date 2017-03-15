gnuradio-buildbot
=================

This repository contains the buildbot configuration for the GNU Radio project.
If all requirements are installed on the local computer it should be able to run the full CI (except auth tokens and keys).

# CI Design

## Overview
The buildbot master will be contained in a docker container and will use an existing Postgres Container or spawn its own to hold runtime data (builds, logs).
If a buildrequest (e.g. through a source change) comes in necessary builds will be triggered and not yet started workers will be spun up through a docker socket. Alternatively already running docker container can be permanently connected to the buildbot master. 

## Builds
If the buildmaster receives a buildrequest the base branch (or the actual branch) is compared to existing development branches (e.g. maint, master, next) and depending on its type the change will be merged into other development branches as well and tested for forward compatibility as well.

## Authentication
To authenticate users the GitHub authentication will be used.

# docker/

This subdirectory contains configuration for the buildbot master to start with `docker-compose`

# master.cfg gr_buildbot/

This subdirectory and configuration file contain the buildbot configuration for the buildbot master
