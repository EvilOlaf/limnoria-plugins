# Jira for Limnoria

Add some description

## Requirements
```
pip install jira
```
https://pypi.org/project/jira/


## Configuration

You will need to configure the following:

```
supybot.plugins.Jira.server            = The server name of your Jira instance. (ex: "https://jira.mysite.com")
```

Not there yet:
```
supybot.plugins.Jira.snarfRegex        = The regular expression used for snarfing Jira issues in chat. The whole of this
                                         expression is what the plugin will use to look up your issue in Jira. 
                                         When setting this from within IRC, you will probably need to use double-quotes 
                                         or the bot will fail to handle your input.
                                         (ex: "(?:(?<=\\s)|^)[A-Z]+-[0-9]+(?:(?=[\\s.?!,])|$) - Capital letters dash numbers")
```

## Usage


TBD