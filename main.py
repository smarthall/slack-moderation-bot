#!/usr/bin/env python

import yaml

from moderator import Bot

config = yaml.load(open('slack.conf', 'r'))

b = Bot(config)
b.run()
