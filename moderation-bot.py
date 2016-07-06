#!/usr/bin/env python
from __future__ import unicode_literals

# TODO: Split this out into nice classes and not one big giant script

import yaml
import time
from slackclient import SlackClient

def do_message(msg):
    if msg['channel'].startswith('C'):
        print sc.api_call('chat.delete', ts=msg['ts'], channel=msg['channel'], as_user=True)

config = yaml.load(open('slack.conf', 'r'))

sc = SlackClient(config['SLACK_TOKEN'])
if sc.rtm_connect():
    while True:
        for event in sc.rtm_read():
            print event
            if event['type'] == u'message':
                do_message(event);
        time.sleep(1)

