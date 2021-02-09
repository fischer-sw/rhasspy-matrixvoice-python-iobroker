#!/usr/bin/python3
#
#        file: recog.py
#
# description: rhasspy MATRIX Voice base class
#

import datetime
import json
import locale
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

    def say_action(self, intent, room, phrases):
        say_string = ''
        now = datetime.datetime.now()
        for phrase in phrases:
            if intent.endswith('Climate') or intent.endswith('Temp') or intent.endswith('Humid'):
                m = re.match('.*{([^}:]+)[}:].*', phrase)
                if not m:
                    continue
                if not m.group(1) in self.config['room_climate'][room].keys():
                    continue
                id = self.config['room_climate'][room][m.group(1)]
                value = float(self.iobroker.get_value(id))
                say_string += phrase.replace(m.group(1), '').format(value)
            elif intent == 'GetTime' or intent == 'GetDate':
                say_string += now.strftime(phrase)
        if say_string:
            self.log.debug('SAY: {}'.format(say_string))
            self.say(say_string)
        return say_string

    def switch_action(self, room, device, state, actions):
        cmd = None
        for action in actions:
            if not device in self.config['room_switch'][room].keys():
                continue
            id = self.config['room_switch'][room][device]
            cmd = action.replace('{device.id}', id).replace('{state}', state)
            self.log.debug('SWITCH: {}'.format(cmd))
            self.iobroker.set_value(cmd)
        return cmd

    def display_action(self, slots, phrases):
        now = datetime.datetime.now()
        for phrase in phrases:
            for slot, value in slots.items():
                phrase = phrase.replace('{' + slot + '}', value)
            if '%' in phrase:
                phrase = now.strftime(phrase)
            self.log.debug('DISPLAY: {}'.format(phrase))
            self.display(phrase)

    def resolve_variables(self, s):
        return s

    def intent_action(self, intent, conf, slots):
        result = None
        if conf < 0.9:
            self.log.warning('confidence {} too low'.format(conf))
            return result
        if intent == 'Alarm':
            if slots['color'] in self.config['colors'].keys():
                color = self.config['colors'][slots['color']]
            hue_xy = { 'red' : [0.7, 0.3], 'yellow': [ 0.48, 0.49 ], 'green' : [ 0.21, 0.71 ], 'blue': [ 0.14, 0.8 ] }
            self.say(slots['color'] + ' Alarm')
            cmd = 'hue.1.Arbeitszimmer.xy={}'.format(hue_xy[color])
            self.iobroker.set_value(cmd)
            cmd = 'hue.1.Arbeitszimmer.alert=lselect'
            self.iobroker.set_value(cmd)
            mv_utils.led_blink(color, 10)
            result = color
        elif intent.startswith('Get'):
            room = 'flachdach'
            if intent.endswith('Climate') or intent.endswith('Temp') or intent.endswith('Humid'):
                if len(slots) > 0 and 'room' in slots.keys():
                    room = slots['room']
                actions = self.config["actions"][intent]
                for action in actions:
                    for key, value in action.items():
                        if key == 'say':
                            result = self.say_action(intent, room, value)            
                        elif key == 'display':
                            self.display_action(slots, value)
            elif intent.endswith('Time') or intent.endswith('Date'):
                for action in self.config["actions"][intent]:
                    for key, value in action.items():
                        if key == 'say':
                            result = self.say_action(intent, room, value)
                        elif key == 'display':
                            self.display_action(slots, value)
        elif intent == 'Switch':
            room = 'arbeitszimmer'
            if len(slots) > 0 and 'room' in slots.keys():
                room = slots['room']
            device = slots['device']
            state = 'false'
            if slots['state'] == 'ein':
                state = 'true'
            self.log.debug('room {} device {} state {} actions {}'.format(room, device, state, self.config["actions"][intent]))
            for action in self.config["actions"][intent]:
                for key, value in action.items():
                    if key == 'switch':
                        result = self.switch_action(room, device, state, value)
                    elif key == 'display':
                        self.display_action(slots, value)
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
        return result

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
