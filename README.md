gnuradio-buildbot
=================

This repository contains the buildbot configuration for the GNU Radio project.
If `docker` and `docker-compose` are available on the local machine you should be able to run the full CI locally. (Except Keys and Webhooks)

# CI Design

## Overview

The buildbot master runs in a very limited alpine container and is connected to a Postgres container.
On receiving a build request a build is kicked off on the master. The master will then spawn required Linux containers to fulfill the build request. Alternatively a permanently running container, VM or remote machine can be used as worker.

## Builds
If the buildmaster receives a buildrequest the base branch (or the actual branch) is compared to existing development branches (e.g. maint, master, next) and depending on its type the change will be merged into other development branches as well and tested for forward compatibility.

## Authentication
To authenticate users the GitHub authentication system is used.

# Configuration structure

For easier maintenance of buildbot the following directory structure was chosen.

## master.cfg

Main configuration file. Imports the `config_module` and returns generated configuration in `config_module` to Twisted.

## master/

Contains the Dockerfile and configuration for the buildbot master to start it with `docker-compose`.

## worker/

Contains Dockerfiles for GNU Radio buildbot worker container images.

## config_module/

Contains actual configuration for builders, schedulers, reporters and workers.
Builder and worker configuration is done in `workers.json` and `builders/builders.json`. Both files are parsed in `__init__.py` and generated builders and workers are appended to appropriate lists.

## gnuradio_buildbot/

Contains custom steps and step sequences for code deduplication in `config_module`. Some of the steps may be upstreamed to `buildbot` in the future.

## data/

Contains extra files to pass into the master for runtime reconfiguration.
