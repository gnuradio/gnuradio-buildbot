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
from gnuradio_buildbot import custom_steps

from buildbot.process.results import SUCCESS
from buildbot.process.results import SKIPPED
import json
import os


_BASEPATH = os.environ.get("BUILDBOT_SRC_BASE", "/tmp")
_PULL_SRC_BASE = os.path.join(_BASEPATH, "pull")


def build_PR():

    create_src = steps.MakeDirectory(
        name="create src directory",
        dir="src")

    clone_step = steps.GitHub(
        name="fetch PR source",
        repourl=util.Property("repository"),
        mode="full",
        method="fresh",
        submodules=True,
        retryFetch=True,
        clobberOnFailure=True,
        workdir="src")

    rm_src_dir = steps.RemoveDirectory(
        dir=util.Interpolate(
            os.path.join(_BASEPATH, "pull",
                         "%(prop:github.number)s", "%(prop:github.base.ref)s")
        ),
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
    )

    copy_src = steps.CopyDirectory(
        name="copy src to srcdir",
        src="src",
        dest=util.Interpolate(
            os.path.join(_BASEPATH, "pull",
                         "%(prop:github.number)s", "%(prop:github.base.ref)s"),
        ),
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
    )
    # load builders.json with definitions on how to build things
    parent_path = os.path.dirname(__file__)
    with open(os.path.join(parent_path, "builders.json"), "r") as builders_file:
        build_config = json.loads(builders_file.read())

    trigger_builds = custom_steps.BuildTrigger(
        name="trigger the right builders",
        build_config=build_config,
        schedulerNames=["trigger"],
        runner="pull",
        set_properties={
            "pr_base": util.Property("github.base.ref"),
            "src_dir": util.Interpolate(os.path.join(
                _PULL_SRC_BASE, "%(prop:github.number)s"))
        },
        updateSourceStamp=False,
        waitForFinish=True
    )

    factory = util.BuildFactory()
    factory.addStep(create_src)
    factory.addStep(clone_step)
    factory.addStep(rm_src_dir)
    factory.addStep(copy_src)
    factory.addStep(trigger_builds)
    return factory
