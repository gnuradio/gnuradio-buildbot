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

from buildbot.process.results import SUCCESS
from buildbot.process.results import SKIPPED
import os


def mergeability_sequence(branch, prev_branch, src_base):
    def condition(step):
        return step.getProperty("merge_"+prev_branch, False)

    fetch_base = steps.ShellCommand(
        name="fetch "+branch+" from upstream",
        command=[
            "git", "fetch", "-t", util.Property("repository"), branch
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
        doStepIf=condition
    )

    create_new_worktree = steps.ShellCommand(
        name="checkout test_merge_"+branch+" branch",
        command=[
            "git", "checkout", "-B", "test_merge_"+branch, "FETCH_HEAD"
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED,
        doStepIf=condition
    )

    merge_new_changes = steps.ShellCommand(
        name="merge test_merge_"+prev_branch+" into test_merge_"+branch,
        command=[
            "git", "merge", "--no-edit", "test_merge_"+prev_branch
        ],
        flunkOnFailure=False,
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED,
        doStepIf=condition
    )

    @util.renderer
    def set_merge_prop(step):
        if step.build.executedSteps[-2].results == SUCCESS:
            return True
        return False

    set_merge_property = steps.SetProperty(
        name="Set merge_"+branch+" to True if merge was successful",
        property="merge_"+branch,
        value=set_merge_prop,
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
        doStepIf=condition)

    sync_submodule = steps.ShellCommand(
        name="sync submodules on test_merge_"+branch,
        command=[
            "git", "submodule", "update", "--init", "--recursive"
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
        doStepIf=condition
    )

    make_src_base = steps.ShellCommand(
        name="create src_base directory for test_merge_"+branch,
        command=[
            "mkdir", "-p", util.Interpolate(
                os.path.join(src_base, "%(prop:github.number)s", branch))
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
        doStepIf=condition
    )

    copy_src = steps.ShellCommand(
        name="copy test_merge_"+branch+" src dir to common src dir",
        command=[
            "rsync", "--delete", "-rLz", "./",
            util.Interpolate(
                os.path.join(src_base, "%(prop:github.number)s", branch))
        ],
        workdir="src",
        hideStepIf=lambda results, s: results == SKIPPED or results == SUCCESS,
        doStepIf=condition,
    )

    result = []
    result.append(fetch_base)
    result.append(create_new_worktree)
    result.append(merge_new_changes)
    result.append(set_merge_property)
    result.append(sync_submodule)
    result.append(make_src_base)
    result.append(copy_src)
    return result
