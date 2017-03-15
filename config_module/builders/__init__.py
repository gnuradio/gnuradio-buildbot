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

from buildbot.plugins import util
from control_PR import build_PR
from control_volk_PR import build_volk_PR
from control_push import build_push
from control_weekly import build_weekly
from build_GR import build_and_test
from build_coverity import build_coverity
from build_coverage import build_coverage


def filterWorkers(workers, what, attr):
    return [w for w in workers
            if attr in w.properties.getProperty(what, [])
            or attr == w.properties.getProperty(what, "")]


def get(workers):
    """
    construct a list of builders with the given list of workers
    """
    builders = []
    builders.append(
        util.BuilderConfig(
            name="pull_request_runner",
            tags=["control", "gnuradio", "pull"],
            workernames=[w.name for w in filterWorkers(workers, "tasks", "control")],
            factory=build_PR())
    )
    builders.append(
        util.BuilderConfig(
            name="volk_pull_request_runner",
            tags=["control", "volk", "pull"],
            workernames=[w.name for w in filterWorkers(workers, "tasks", "control")],
            factory=build_volk_PR()))
    builders.append(
        util.BuilderConfig(
            name="repo_push_runner",
            tags=["control", "push"],
            workernames=[w.name for w in filterWorkers(workers, "tasks", "control")],
            factory=build_push())
    )

    builders.append(
        util.BuilderConfig(
            name="weekly_runner",
            tags=["control", "weekly"],
            workernames=[w.name for w in filterWorkers(workers, "tasks", "control")],
            factory=build_weekly())
    )

    build_workers = filterWorkers(workers, "tasks", "build")
    distros = [w.properties.getProperty("distro") for w in build_workers
               if w.properties.getProperty("distro", None)]
    distros = list(set(distros))
    for distro in distros:
        builders.append(
            util.BuilderConfig(
                name="build_"+distro,
                tags=["build"],
                workernames=[w.name for w in
                             filterWorkers(build_workers, "distro", distro)],
                factory=build_and_test())
            )
    coverity_workers = filterWorkers(workers, "tasks", "coverity")
    builders.append(
        util.BuilderConfig(
            name="test_coverity",
            tags=["test", "coverity"],
            workernames=[w.name for w in coverity_workers],
            factory=build_coverity()
        )
    )
    builders.append(
        util.BuilderConfig(
            name="test_coverage",
            tags=["test", "coverage"],
            workernames=[w.name for w in coverity_workers],
            factory=build_coverage()))
    return builders
