#!/usr/bin/python3
#
#        file: recog.py
#
# description: rhasspy MATRIX Voice base class
#

import datetime
import json
import logging
import os
import re
import sys

import rhasspy_matrix_voice
import mv_utils

class Recognizer(rhasspy_matrix_voice.RhasspyMatrixVoice):

    def __init__(self, config_file, logger=None):
        super(Recognizer, self).__init__(config_file, logger)

    def do_action(self, action, command):
        self.log.info('ACTION {} {}'.format(action, command))

    def intent_action(self, intent, conf, slots):
        if conf > 0.9:
            now = datetime.datetime.now()
            if intent.startswith('Get'):
                action = self.config["actions"][intent].split('|')
                if intent.endswith('Time'):
                    self.say(now.strftime(action[1]))
                elif intent.endswith('Date'):
                    self.say(now.strftime(action[1]))
                elif intent.endswith('Temp'):
                    m = re.match('.*{([^}]+)}.*', action[1])
                    if m:
                        id = m.group(1)
                    temp = self.iobroker.get_value(id)
                    self.say(action[1].replace(id, '').format(temp))
            elif intent == 'Switch':
                state = 'false'
                if slots['state'] == 'ein':
                    state = 'true'
                cmd = 'hue.1.Arbeitszimmer.on={}'.format(state)
                self.log.info(cmd)
                self.iobroker.set_value(cmd)
            elif intent == 'ChangeLightBrightness':
                brightness = slots["brightness"] * 254 / 100
                cmd = 'hue.1.Arbeitszimmer.bri={}'.format(brightness)
                self.log.info(cmd)
                self.iobroker.set_value(cmd)
            elif intent == 'SetTimer':
                timer = slots["timer"]
                if slots["unit"] == "Minuten":
                    timer *= 60
                mv_utils.led_timer(timer)
            elif intent == 'StartMusic':
                channels = { 'WDR2' : '1', 'WDR5' : '2' }
                devices = { 'HEOS' : 'heos.0.players.-526897417' }
                device = devices[slots["device"]]
                channel = channels[slots["channel"]]
                cmd = device + ".command=set_play_state%26state%3Dplay%26preset%3D" + channel
                self.log.info(cmd)
                self.iobroker.set_value(cmd)
                cmd = "{}.muted=false".format(device)
                self.log.info(cmd)
                self.iobroker.set_value(cmd)
        else:
            log.warning('nothing recognized')

if __name__ == '__main__':
    import argparse
    import calendar
    import locale

    self = os.path.basename(sys.argv[0])
    myName = os.path.splitext(self)[0]
    log = logging.getLogger(myName)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config', default='config.json', help='config file')
    parser.add_argument('-d', '--debug', action='store_true', help='debug execution')
    parser.add_argument('-L', '--locale', default='de_DE.UTF-8', help='locale')
    args = parser.parse_args(sys.argv[1:])
    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    locale.setlocale(locale.LC_ALL, args.locale)
    calendar.setfirstweekday(calendar.MONDAY)

    rec = Recognizer(args.config, logger=log)
    rec.run()
