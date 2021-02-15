import logging
import os
import sys
import threading
import time
import unittest

from mv_utils import MatrixVoiceUtils

self = os.path.basename(sys.argv[0])
myName = os.path.splitext(self)[0]
log = logging.getLogger(myName)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log.setLevel(logging.DEBUG)

mv = None

def setUpModule():
    global mv
    mv = MatrixVoiceUtils()

def tearDownModule():
    global mv
    mv = None

#@unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):

    def test_blink(self):
        self.assertTrue(mv.led_blink("green", 3))
        threads = threading.enumerate()
        self.assertGreater(len(threads), 0)
        self.assertTrue(threads[1].is_alive())
        self.assertTrue("blink" in threads[1].name)
        mv.join()

#@unittest.skip("Skipping Test02")
class Test02(unittest.TestCase):

    def test_timer(self):
        self.assertTrue(mv.led_timer(5))
        threads = threading.enumerate()
        self.assertGreater(len(threads), 0)
        self.assertTrue(threads[1].is_alive())
        self.assertTrue("timer" in threads[1].name)
        mv.join()

#@unittest.skip("Skipping Test03")
class Test03(unittest.TestCase):

    def test_listen(self):
        self.assertTrue(mv.listen())
        threads = threading.enumerate()
        self.assertGreater(len(threads), 0)
        self.assertTrue(threads[1].is_alive())
        self.assertTrue("listen" in threads[1].name)
        time.sleep(3)
        mv.stop_thread = True
        mv.join()

#@unittest.skip("Skipping Test04")
class Test04(unittest.TestCase):

    def test_blink_blink(self):
        self.assertTrue(mv.led_blink("yellow", 3))
        self.assertFalse(mv.led_blink("red", 3))
        mv.join()

if __name__ == '__main__':
    unittest.main(verbosity=2)
