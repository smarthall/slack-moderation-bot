import time
from slackclient import SlackClient

MODERATED_TYPES = (
    'none',
    'me_message',
)

SCRAPED_TYPES = (
    'none',
)

MODERATED_MESSAGE = "Hey, I deleted one of your messages. If you want to announce something say it with `ANNOUNCE:` at the start in a different channel."
ANNOUNCE_MESSAGE = "Announcing: {original}"
TYPING_MESSAGE = "Whoa, stop typing, that channel is moderated."

def msg_user(msg):
    if msg.get('user', False):
        return msg['user']
    elif msg.get('previous_message', False) and msg['previous_message'].get('user', False):
        return msg['previous_message']['user']

    print('UNKNOWN USER FOR MESSAGE:')
    print(msg)

    return None

class Bot:
    def __init__(self, config):
        self.sc = SlackClient(config['token'])
        self.channel_config = config['channels']
        self.moderated_channels = []
        self.scraped_channels = []

        self._usercache = {}

        # Even bots have to find themselves
        response = self.sc.api_call('auth.test')
        self.own_userid = response['user_id']

    def run(self):
        if self.sc.rtm_connect():
            while True:
                for event in self.sc.rtm_read():
                    print(event)
                    if event['type'] == 'message':
                        self.do_message(event)
                    elif event['type'] == 'hello':
                        self.do_hello(event)
                    elif event['type'] == 'user_typing':
                        self.do_typing(event)
                time.sleep(1)

    def got_channels(self, chanlist):
        for chan in chanlist:
            if chan['name'] in self.channel_config['moderated']:
                self.moderated_channels.append(chan['id'])
                if not chan['is_member']:
                    print(self.sc.api_call('channels.join', name=chan['name']))

            elif chan['name'] in self.channel_config['scraped']:
                self.scraped_channels.append(chan['id'])
                if not chan['is_member']:
                    print(self.sc.api_call('channels.join', name=chan['name']))

            elif chan['is_member'] and not chan['is_general'] and not chan['is_archived']:
                print(self.sc.api_call('channels.leave', name=chan['id']))


    def do_hello(self, event):
        response = self.sc.api_call('channels.list')
        self.got_channels(response['channels'])

    def do_message(self, msg):
        # Messages in moderated channels that we didn't write
        if (
                msg.get('subtype', 'none') in MODERATED_TYPES and
                msg['channel'] in self.moderated_channels and
                msg_user(msg) != self.own_userid
           ):
            self.do_message_moderation(msg)
        
        elif (
                msg.get('subtype', 'none') in SCRAPED_TYPES and
                msg['channel'] in self.scraped_channels and
                msg_user(msg) != self.own_userid and
                msg.get('text', '').startswith('ANNOUNCE:')
             ):
            self.do_scrape_message(msg)

    def do_typing(self, event):
        if event['channel'] in self.moderated_channels:
            self.do_warn_user(event)

    def do_warn_user(self, event):
        response = self.sc.api_call('im.open', user=event['user'])
        imchan = response['channel']['id']
        message = TYPING_MESSAGE.format({
        })
        print(self.sc.api_call('chat.postMessage', channel=imchan, text=message, as_user=True))

    def do_message_moderation(self, msg):
        print(self.sc.api_call('chat.delete', ts=msg['ts'], channel=msg['channel'], as_user=True))
        response = self.sc.api_call('im.open', user=msg_user(msg))
        imchan = response['channel']['id']
        message = MODERATED_MESSAGE.format({
        })
        print(self.sc.api_call('chat.postMessage', channel=imchan, text=message, as_user=True))

    def do_scrape_message(self, msg):
        message = ANNOUNCE_MESSAGE.format(
                original=msg['text'][10:],
        )
        for chan in self.moderated_channels:
            print(self.sc.api_call('chat.postMessage', channel=chan, text=message, as_user=True))

