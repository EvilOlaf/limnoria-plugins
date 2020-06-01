###
# Copyright (c) 2013, Adam Harwell
# Copyright (c) 2020, Werner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import os
import re

import supybot.callbacks as callbacks
import supybot.conf as conf
import supybot.ircutils as ircutils
import supybot.plugins as plugins
import supybot.utils as utils
import yaml
from jira import JIRA
from time import sleep
from supybot.commands import *
from supybot import log

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Jira')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x): return x


class Jira(callbacks.Plugin):
    """This plugin communicates with Jira. It will automatically snarf
    Jira ticket numbers, and reply with some basic information
    about the ticket. It can also close and comment on Jira tasks."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Jira, self)
        self.__parent.__init__(irc)
        self.server = self.registryValue('server')

    def getissue(self, irc, msg, args, text):
        """Get a Jira Issue"""
        jira = JIRA(self.server)
        try:
            issue = jira.issue(text)
        except:
            replytext = ("Either invalid or unknown issue.")
            irc.reply(replytext, prefixNick=False)
            return
        recentDate = issue.fields.created
        splitdate = recentDate.split('T')
        replytext = ("{0}: {1}, reported by {2} at {3}. Status: {4}.".format(
            issue.key, issue.fields.summary, issue.fields.creator, splitdate[0], issue.fields.status))
        irc.reply(replytext, prefixNick=False)
    getissue = wrap(getissue, ['text'])

    def recent(self, irc, msg, args):
        """Fetch the most recent issue"""
        jira = JIRA(self.server)
        for issue in jira.search_issues('project=Armbian order by created',  maxResults=1):
            recentDate = issue.fields.created
            splitdate = recentDate.split('T')
            replytext = ("{0}: {1}, reported by {2} at {3}. Status: {4}.".format(
                issue.key, issue.fields.summary, issue.fields.creator, splitdate[0], issue.fields.status))
            irc.reply(replytext, prefixNick=False)
        log.debug("test")
    recent = wrap(recent)

    def recentonly(self, irc, msg, args):
        """Fetch the most recent issue"""
        jira = JIRA(self.server)

        script_dir = os.path.dirname(__file__)
        rel_path = "data/tmp/issue.txt"
        abs_file_path = os.path.join(script_dir, rel_path)

        try:
            with open(abs_file_path, "r+", encoding="utf-8") as file:
                for line in file:
                    lastknownissue = line
                log.error(lastknownissue)
        except:
            with open(abs_file_path, "w+", encoding="utf-8") as file:
                pass

        for issue in jira.search_issues('project=Armbian order by created',  maxResults=1):
            if issue.key != lastknownissue:
                recentDate = issue.fields.created
                splitdate = recentDate.split('T')
                replytext = ("{0}: {1}, reported by {2} at {3}. Status: {4}.".format(
                    issue.key, issue.fields.summary, issue.fields.creator, splitdate[0], issue.fields.status))
                irc.reply(replytext, prefixNick=False)
                with open(abs_file_path, "w+", encoding="utf-8") as file:
                    file.write(issue.key)

            else:
                replytext = ("no new issue")
                irc.reply(replytext, prefixNick=False)
    recentonly = wrap(recentonly)


'''
    def issues(self, irc, msg, args, search_text):
        """<search_text>

        Searches Jira issue summaries for <search_text>.
        """
        replies = []
        issues = self.jira[self.user].search_issues(
            "summary ~ '{0}'".format(search_text))
        for issue in issues:
            try:
                assignee = issue.fields.assignee.displayName
            except:
                assignee = "Unassigned"

            displayTime = display_time(issue.fields.timeestimate)
            url = ''.join((self.server, 'browse/', issue.key))

            values = {"type": issue.fields.issuetype.name,
                      "key": issue.key,
                      "summary": issue.fields.summary,
                      "status": _c(_b(issue.fields.status.name), "green"),
                      "assignee": _c(assignee, "blue"),
                      "displayTime": displayTime,
                      "url": '',
                      }
            replies.append(self.template % values)
        if replies:
            irc.reply('|| '.join(replies), prefixNick=False)
        else:
            irc.reply("No issues found matching '{0}'.".format(search_text))
        return
    issues = wrap(issues, ['text'])
'''

Class = Jira

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
