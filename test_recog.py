import calendar
import locale
import logging
import os
import sys
import time
import unittest

from recog import Recognizer

self = os.path.basename(sys.argv[0])
myName = os.path.splitext(self)[0]
log = logging.getLogger(myName)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log.setLevel(logging.DEBUG)

rec = None

def setUpModule():
    global rec
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    calendar.setfirstweekday(calendar.MONDAY)
    rec = Recognizer('config.json', logger=log)

def tearDownModule():
    global rec
    rec = None

#@unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):

    def test_config(self):
        self.assertTrue("rhasspy" in rec.config.keys())
        self.assertTrue("actions" in rec.config.keys())

#@unittest.skip("Skipping Test02")
class Test02(unittest.TestCase):

    def test_intent_action_none(self):
        self.assertIsNone(rec.intent_action("anything", 0.1, {}))

    @unittest.skip("Skipping Test02 alarm yellow")
    def test_intent_action_alarm_yellow(self):
        self.assertEqual("yellow", rec.intent_action("Alarm", 0.95, { 'color': 'gelber' }))

    @unittest.skip("Skipping Test02 alarm red")
    def test_intent_action_alarm_red(self):
        self.assertEqual("red", rec.intent_action("Alarm", 0.95, { 'color': 'roter' }))

@unittest.skip("Skipping Test03 gettime,getdate")
class Test03(unittest.TestCase):

    def test_intent_action_gettime(self):
        result = rec.intent_action("GetTime", 0.95, {})
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Es ist "))

    @unittest.skip("Skipping Test02 getdate")
    def test_intent_action_getdate(self):
        result = rec.intent_action("GetDate", 0.95, {})
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Heute ist "))

@unittest.skip("Skipping Test04 getclimate")
class Test04(unittest.TestCase):

    def test_intent_action_getclimate_study(self):
        result = rec.intent_action("GetClimate", 0.95, { 'room': 'arbeitszimmer' })
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Es sind"))
        self.assertTrue("Grad" in result)
        self.assertTrue("Luftfeuchtigkeit" in result)

    def test_intent_action_getclimate_kitchen(self):
        result = rec.intent_action("GetClimate", 0.95, { 'room': 'küche' })
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Es sind"))
        self.assertTrue("Grad" in result)

    def test_intent_action_gethumid_terrace(self):
        result = rec.intent_action("GetRoomHumid", 0.95, { 'room': 'terrasse' })
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Es sind"))
        self.assertTrue("Luftfeuchtigkeit" in result)

    def test_intent_action_gettemp(self):
        result = rec.intent_action("GetTemp", 0.95, {})
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Es sind"))
        self.assertTrue("Grad" in result)

    def test_intent_action_gettemp_floor(self):
        result = rec.intent_action("GetRoomTemp", 0.95, { 'room': 'flur' })
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("Es sind"))
        self.assertTrue("Grad" in result)

#@unittest.skip("Skipping Test05 getswitch")
class Test05(unittest.TestCase):

    def test_intent_action_switch_globe(self):
        result = rec.intent_action("Switch", 0.95, { 'room': 'arbeitszimmer', 'device': 'globus', 'state': 'ein' })
        self.assertIsNotNone(result)
        self.assertTrue("brennenstuhl2d" in result)
        time.sleep(5)
        result = rec.intent_action("Switch", 0.95, { 'room': 'arbeitszimmer', 'device': 'globus', 'state': 'aus' })
        self.assertIsNotNone(result)
        self.assertTrue("brennenstuhl2d" in result)

    def test_intent_action_switch_heos(self):
        result = rec.intent_action("Switch", 0.95, { 'room': 'arbeitszimmer', 'device': 'heos', 'state': 'ein' })
        self.assertIsNotNone(result)
        self.assertTrue("brennenstuhl2c" in result)
        time.sleep(5)
        result = rec.intent_action("Switch", 0.95, { 'room': 'arbeitszimmer', 'device': 'heos', 'state': 'aus' })
        self.assertIsNotNone(result)
        self.assertTrue("brennenstuhl2c" in result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
