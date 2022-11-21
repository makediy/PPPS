# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from machine import UART,Pin,SoftI2C,ADC,Timer
import time
from neopixel import NeoPixel
from emp_wifi import Wifi
from emp_webrepl import WebREPL
from emp_utils import webrepl_pass
from emp_utils import post_ip
import webrepl

if __name__ == '__main__':
    Wifi.connect()
    try:
        post_ip(Wifi.ifconfig()[0][0])
        #webrepl.start(password='123') 
    except ImportError:
        pass
