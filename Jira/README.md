# Jira for Limnoria

tl;dr: Snarfs issue ids by configurable regex (JRA-123 for example) and allows searching for issues by summary.
Also checks recurringly for new issues and pastes it into a channel when found.


## Requirements
```
pip install jira
```
https://pypi.org/project/jira/


## Configuration

You will need to configure the following:

```
supybot.plugins.Jira.server            = The server name of your Jira instance. (ex: "https://jira.mysite.com")

supybot.plugins.Jira.snarfRegex        = The regular expression used for snarfing Jira issues in chat. The whole of this
                                         expression is what the plugin will use to look up your issue in Jira. 
                                         When setting this from within IRC, you will probably need to use double-quotes 
                                         or the bot will fail to handle your input.
                                         (ex: "(?:(?<=\\s)|^)[A-Z]+-[0-9]+(?:(?=[\\s.?!,])|$) - Capital letters dash numbers")

supybot.plugins.Jira.channel            = Target channel where the bot should announce newly created issues

supybot.plugins.Jira.snarfChannel       = Target channel where the bot is allowed to snarf Jira issues

```

## Usage

Create a folder named `Jira` in your plugins folder and put the contents there.
Load the plugin.
May throw errors at beginning if not configured properly.
