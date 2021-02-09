#
#        file: rhasspy_matrix_voice.py
#
# description: rhasspy MATRIX Voice base class
#

import datetime
import logging
import os
import threading
import time
import json
import sys

import paho.mqtt.client as paho
from iobroker import IoBroker

import mv_utils

class RhasspyMatrixVoice:

    def __init__(self, config_file, logger=None):
        if logger == None:
            self.log = logging.getLogger(__file__)
        else:
            self.log = logger
        with open(config_file) as f:
            self.config = json.load(f)
            self.mqtt_broker = self.config["mqtt"]["host"]
            self.mqtt_user = self.config["mqtt"]["user"]
            self.mqtt_password = self.config["mqtt"]["password"]
            self.topics = self.config["topics"]

        self.iobroker = IoBroker(self.config['iobroker']['host'], self.config['iobroker']['port'], logger=self.log, get_objects=False)

        self.stop_thread = False
        self.blink_thread = None

        self.mqtt = paho.Client(self.config["rhasspy"]["slave"]["host"])
        self.rhasspy_client_id = self.config["rhasspy"]["slave"]["id"]

    def listening(self):
        everloop = ['black'] * mv_utils.led_num()
        everloop[0] = {'b':80}
        everloop[1] = {'b': 60}
        everloop[2] = {'b': 20}
        everloop[3] = {'b': 10}

        everloop[9] = {'b': 80}
        everloop[10] = {'b': 60}
        everloop[11] = {'b': 20}
        everloop[12] = {'b': 10}

        while not self.stop_thread:
            everloop.append(everloop.pop(0))
            mv_utils.led_set(everloop)
            time.sleep(0.070)

    def start_listening(self, message):
        if not self.blink_thread is None:
            return
        self.log.info("Listening started")
        self.display("Listen...")
        self.stop_thread = False
        self.blink_thread = threading.Thread(target=self.listening)
        self.blink_thread.start()

    def stop_listening(self, message):
        if self.blink_thread is None:
                return
        self.stop_thread = True
        self.blink_thread.join()
        self.blink_thread = None
        mv_utils.led_reset()
        self.log.info("Listening stopped")
        self.display("Listen done")

    def display(self, message):
        if 'display' in self.config.keys():
            topic = self.config['display']['topic']
            self.log.debug('MQTT: {} {}'.format(topic, message))
            self.mqtt.publish(topic, message.encode())

    def say(self, text):
        topic = "hermes/tts/say"
        payload = { "text": text, "siteId": self.rhasspy_client_id }
        self.mqtt.publish(topic, json.dumps(payload).encode())

    def on_intent(self, message):
        mv_utils.led_blink("green", 1)
        payload = json.loads(message.payload.decode())
        intent = payload["intent"]["intentName"]
        conf = payload["intent"]["confidenceScore"]
        slots = {}
        if "slots" in payload.keys():
            for x in payload["slots"]:
                slots[x["slotName"]] = x["value"]["value"]        
        self.log.debug('{} {} {}'.format(intent, conf, slots))
        self.intent_action(intent, conf, slots)

    def intent_action(self, intent, conf, slots):
        self.log.error('empty base class method, override in derived class')

    def on_message(self, client, userdata, message):
        topic = message.topic
        if topic in self.topics:
            command = self.topics[topic]
            getattr(self, command)(message)
            
    def run(self):
        self.blink_thread = None
        self.stop_thread = False
        mv_utils.led_reset()
        self.mqtt.on_message = self.on_message
        self.log.debug("connecting to MQTT broker " + self.mqtt_broker)
        self.mqtt.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.mqtt.connect(self.mqtt_broker)
        self.log.debug("subscribing topics")
        for topic in self.topics.keys():
            self.mqtt.subscribe(topic)
        self.mqtt.loop_forever()
