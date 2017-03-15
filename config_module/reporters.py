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

from buildbot.plugins import reporters, util
import os


@util.renderer
def get_context(prop):
    buildername = prop.getProperty("virtual_builder_name", None)
    if buildername is None:
        buildername = prop.getProperty("buildername")
    context = "bb/"+buildername
    return context

def get():
    reps = []
    github_status = reporters.GitHubStatusPush(token=os.environ.get("BUILDBOT_ACCESS_TOKEN"),
                                               context=get_context,
                                               startDescription='Build started.',
                                               endDescription='Build done.',
                                               verbose=True)
    reps.append(github_status)
    return reps
