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
from time import sleep

import supybot.callbacks as callbacks
import supybot.conf as conf
import supybot.ircutils as ircutils
import supybot.plugins as plugins
import supybot.utils as utils
import yaml
from jira import JIRA
from time import sleep
from supybot.commands import wrap
from supybot import log
import supybot.schedule as schedule
import supybot.ircmsgs as ircmsgs

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
    about the ticket."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Jira, self)
        self.__parent.__init__(irc)
        self.server = self.registryValue('server')

        self.checkTime = 30  # move to config

        try:
            schedule.removeEvent('recent')
        except KeyError:
            pass

        def myEventCaller():
            self.recentOnly(irc)
        schedule.addPeriodicEvent(
            myEventCaller, self.checkTime, 'recent')
        self.irc = irc

    def searchissue(self, irc, msg, args):
        """Search for JIRA issues by keyword/s in issue summary. Outputs up to three results."""
        jira = JIRA(self.server)
        if len(args) == 0:
            replytext = (
                "Search for JIRA issues by keyword/s. Outputs up to three results. Example: \x02searchissue Allwinner H6 sound")
            irc.reply(replytext, prefixNick=False)
            return

        # construct search string for JIRA API
        searchstring = "project=Armbian "
        for arg in args:
            searchstring += " AND summary ~ " + arg
        searchstring += " order by created"

        resultlist = []
        for issue in jira.search_issues(searchstring, maxResults=3):
            recentDate = issue.fields.created
            splitdate = recentDate.split('T')
            resultlist.append([issue.key, issue.fields.issuetype, issue.fields.summary.strip(
            ), issue.fields.creator, splitdate[0], issue.fields.status])
        if len(resultlist) == 0:
            replytext = ("\x02Nothing found.")
            irc.reply(replytext, prefixNick=False)
        else:
            for issue in resultlist:
                replytext = ("\x1F\x02\x034{0}\x0F\x03 \x02\x036[{1}] \x03\"{2}\" \x0Freported by \x02\x033{3}\x03\x0F at \x02{4}\x0F. Status: \x1F\x02{5}\x0F".format(
                    issue[0], issue[1], issue[2], issue[3], issue[4], issue[5]))
                irc.reply(replytext, prefixNick=False)
    #searchissue = wrap(searchissue, ['text'])

    def doPrivmsg(self, irc, msg):
        if callbacks.addressed(irc, msg):
            return
        snarfChannel = self.registryValue('snarfChannel')
        if not msg.channel == snarfChannel:
            return

        """
        log.error(msg.channel)
        log.error(msg.nick)
        log.error(msg.args[1])
        log.error(self.registryValue('snarfRegex'))
        log.error(re.search(self.registryValue('snarfRegex'), msg.args[1]))
        """
        x = re.search(self.registryValue('snarfRegex'), msg.args[1])
        if x:
            jira = JIRA(self.server)
            try:
                issue = jira.issue(x.group(0))
                recentDate = issue.fields.created
                splitdate = recentDate.split('T')
                replytext = ("\x1F\x02\x034{0}\x0F\x03 \x02\x036[{1}] \x03\"{2}\" \x0Freported by \x02\x033{3}\x03\x0F at \x02{4}\x0F. Status: \x1F\x02{5}\x0F".format(
                    issue.key, issue.fields.issuetype, issue.fields.summary.strip(), issue.fields.creator, splitdate[0], issue.fields.status))
                # .strip() to get rid of accidential added leading or trailing whitespaces in issue summary
                irc.reply(replytext, prefixNick=False)
            except:
                replytext = (
                    "Detected regex match for Armbian issue: \x1F\x02\x034{0}\x0F\x03. Could not find it on Jira though. :-(".format(x.group(0)))
                irc.reply(replytext, prefixNick=False)
                return

    def recent(self, irc, msg, args):
        """Fetch the most recent issue"""
        jira = JIRA(self.server)
        for issue in jira.search_issues('project=Armbian order by created',  maxResults=1):
            recentDate = issue.fields.created
            splitdate = recentDate.split('T')
            replytext = ("\x1F\x02\x034{0}\x0F\x03 \x02\x036[{1}] \x03\"{2}\" \x0Freported by \x02\x033{3}\x03\x0F at \x02{4}\x0F. Status: \x1F\x02{5}\x0F".format(
                issue.key, issue.fields.issuetype, issue.fields.summary.strip(), issue.fields.creator, splitdate[0], issue.fields.status))
            irc.reply(replytext, prefixNick=False)
    recent = wrap(recent)

    def recentOnly(self, irc):
        """Fetch the most recent issue
        Not a real command, just used for scheduled recurring search"""
        jira = JIRA(self.server)

        # There must be a more decent way to read the file that consist of one line only and
        # to get rid of the file at all and keep that in memory.

        script_dir = os.path.dirname(__file__)
        rel_path = "issue.txt"
        abs_file_path = os.path.join(script_dir, rel_path)

        try:
            with open(abs_file_path, "r+", encoding="utf-8") as file:
                for line in file:
                    lastknownissue = line
                logmsg = "Last known issue key:" + lastknownissue
                log.debug(logmsg)
        except:
            with open(abs_file_path, "w+", encoding="utf-8") as file:
                lastknownissue = ""
                log.debug("Created empty issue temp file.")

        for issue in jira.search_issues('project=Armbian order by created',  maxResults=1):
            if issue.key != lastknownissue:
                recentDate = issue.fields.created
                splitdate = recentDate.split('T')
                replytext = ("\x1F\x02\x034{0}\x0F\x03 \x02\x036[{1}] \x03\"{2}\" \x0Freported by \x02\x033{3}\x03\x0F at \x02{4}\x0F. Status: \x1F\x02{5}\x0F".format(
                    issue.key, issue.fields.issuetype, issue.fields.summary.strip(), issue.fields.creator, splitdate[0], issue.fields.status))
                # irc.reply(replytext, prefixNick=False) # shall not be used in schedule events
                irc.queueMsg(ircmsgs.privmsg(
                    self.registryValue('channel'), replytext))
                with open(abs_file_path, "w+", encoding="utf-8") as file:
                    file.write(issue.key)

            else:
                log.debug(
                    "Recurring new issue search successful. No new issue found.")


Class = Jira
