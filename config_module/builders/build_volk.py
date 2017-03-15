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

from buildbot.plugins import steps
from buildbot.plugins import util

import json
import os

env = {
    "PATH": ["/usr/lib/ccache/", "/usr/lib64/ccache", "${PATH}"],
    "CCACHE_DIR": util.Interpolate(
        os.path.join("/cache", "%(prop:distro)s", "ccache")
    ),
}


def build_and_test():
    remove_build = steps.RemoveDirectory("build")
    create_build = steps.MakeDirectory("build")
    cmake_step = steps.CMake(
        path=util.Property("src_dir"),
        definitions=util.Property("cmake_defs", {}),
        options=util.Property("cmake_opts", []),
        workdir="build",
        env=env
    )

    @util.renderer
    def join_make_opts(props):
        make_opts = props.getProperty("make_opts", [])
        return ["make"] + make_opts

    make_step = steps.Compile(
        command=join_make_opts,
        workdir="build",
        env=env
    )

    def parse_exclude_file(rc, stdout, stderr):
        exclude_tests = json.loads(stdout)
        return {"test_excludes": exclude_tests}


    load_exclude_file = steps.SetPropertyFromCommand(
        command=["cat", os.path.join("/config", "test_excludes.json")],
        extract_fn=parse_exclude_file,
        doStepIf=lambda steps: steps.getProperty("exclude_file", False)
    )

    @util.renderer
    def parse_test_excludes(props):
        command = ["ctest", "--output-on-failure"]
        excludes = props.getProperty("test_excludes", None)
        if excludes is not None:
            command += ["-E", "|".join(excludes)]
        return command

    test_step = steps.Test(
        command=parse_test_excludes,
        workdir="build"
    )

    factory = util.BuildFactory()
    factory.addStep(remove_build)
    factory.addStep(create_build)
    factory.addStep(load_exclude_file)
    factory.addStep(cmake_step)
    factory.addStep(make_step)
    factory.addStep(test_step)
    return factory
