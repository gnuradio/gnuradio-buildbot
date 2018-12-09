# Copyright 2017 Andrej Rode
#
# This file is part of gnuradio-buildbot
#
# gnuradio-buildbot is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# gnuradio-buildbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import json
import os

from buildbot.plugins import worker
from builtins import range
from six import iteritems


class GRWorker(worker.Worker):
    def __init__(self, name, properties, *args, **kwargs):
        password = "grbuildbot",
        kwargs["properties"] = properties

        super(GRWorker, self).__init__(name, password, *args, **kwargs)


class GRLatentWorker(worker.DockerLatentWorker):
    def __init__(self, name, image, properties, *args, **kwargs):
        password = "grbuildbot"

        kwargs["image"] = str(image)

        docker_host = "unix://var/run/docker.sock"
        kwargs.setdefault("docker_host", docker_host)

        hostconfig = kwargs.get("hostconfig", {})
        hostconfig.setdefault(
            "network_mode", "bb-internal"
        )
        hostconfig.setdefault(
            "volumes_from", ["bb-data"]
        )
        kwargs["hostconfig"] = hostconfig
        kwargs["properties"] = properties
        kwargs["followStartupLogs"] = True

        super(GRLatentWorker, self).__init__(name, password, *args, **kwargs)


def createWorkers(config_path):
    workers = []
    with open(config_path) as f:
        config_data = f.read()
    config_data = json.loads(config_data)
    master_fqdn = config_data.get("masterFQDN", None)
    worker_config = config_data.get("workers")
    for os_type, os_config in iteritems(worker_config):
        for os_flavour, flavour_config in iteritems(os_config):
            for n in range(flavour_config.get("workers", 1)):
                name = "_".join([os_flavour, str(n)])
                props = flavour_config.get("properties", {})
                props.setdefault("os", os_type)
                props.setdefault("distro", os_flavour)
                props.setdefault("masterFQDN", master_fqdn)
                if "image" in flavour_config:
                    worker = GRLatentWorker(name, flavour_config.get("image"), props)
                else:
                    worker = GRWorker(name, props)
                workers.append(worker)
    return workers
