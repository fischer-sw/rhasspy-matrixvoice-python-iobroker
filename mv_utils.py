#
#        file: mv_utils.py
#
# description: MATRIX Voice utility functions
#

import math
import time

from matrix_lite import led

def led_num():
    return led.length

def led_set(loop):
    led.set(loop)

def led_reset():
    everloop = ['black'] * led.length
    led.set(everloop)

def blink_value(frequency, counter):
    return round(max(0, (math.sin(frequency*counter+(math.pi/180*270))*155+155)/10))

def led_blink(color, times):
    frequency = 0.375
    blink_time = (2*math.pi)/frequency
    counter = 0.0
    ledAdjust = 1.01
    everloop = [] * led.length
    r = 0
    g = 0
    b = 0
    w = 0

    if times == '':
        times = 0

    while counter < times*blink_time:

        if color == '':
            r = 0
            w = blink_value(frequency, counter)
            g = 0
            b = 0
        else:
            if color == "yellow":
                r = blink_value(frequency, counter)
                g = blink_value(frequency, counter)
                b = 0
                w = 0
            if color == "blue":
                r = 0
                b = blink_value(frequency, counter)
                g = 0
                w = 0
            if color == "red":
                b = 0
                r = blink_value(frequency, counter)
                g = 0
                w = 0
            if color == "green":
                r = 0
                g = blink_value(frequency, counter)
                b = 0
                w = 0

        counter += ledAdjust

        leds = [{'r':r, 'g':g, 'b':b, 'w':w}]*led.length
        #print(leds)

        everloop[0:led.length] = leds 
        #print(everloop)
        led.set(everloop)

        time.sleep(0.060)

    everloop = ['black'] * led.length
    led.set(everloop)

def led_timer(timeout):
    color = {'r':0, 'g':10, 'b':0, 'w':0 }
    everloop = [color] * led.length
    led.set(everloop)

    for i in range(led.length):
        time.sleep(timeout/led.length)
        last_led = led.length-1-i
        
        if i == led.length-11:
            color = {'r':10, 'g':10, 'b':0, 'w':0 }
        if i == led.length-6:
            color = {'r':20, 'g':0, 'b':0, 'w':0 }
        everloop[0:last_led] = [color]*last_led
        
        everloop[last_led] = 'black'
        led.set(everloop)

    time.sleep(timeout/led.length)
    led_blink("green",3)
