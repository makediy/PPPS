from machine import I2C, Pin
from oled import OLED12864_I2C
import os

import time
i2c = SoftI2C(scl=Pin(11,Pin.IN, Pin.PULL_UP), sda=Pin(12,Pin.IN, Pin.PULL_UP), freq=250000)

oled = OLED12864_I2C(i2c)
oled.Font('Font_12x24')
oled.clear()
f=open('12.bin','r')
ss = bytearray(1025)
ss[0] = 0x40
s=bytes(f.read(),'utf-8')
len(s)
p=0
for i in range(1, len(s)):
    ss[i+p*80]=s[i-1]
    if i%48==0: p=p+1
oled.set_pos(40,2)
oled.i2c.writeto(oled.ADDR, ss)
# time.sleep(5)
# oled.clear()
# oled.text(32, 2, '00.0V')
# oled.text(32, 5, '00.0A')
# oled.HZ24(0,2,0)
# oled.HZ24(0,5,1)
# 
# while 1:
#     oled.HZ16(112,0,14)
#     oled.HZ16(32,0,7)
#     oled.HZ16(48,0,1)
#     time.sleep(5)
#     oled.HZ24(0,2,2)
#     oled.HZ24(0,5,3)
#     oled.HZ16(112,0,15)
#     oled.HZ16(32,0,7)
#     oled.HZ16(48,0,2)
#     time.sleep(5)
#     oled.HZ16(112,0,16)
#     oled.HZ16(32,0,12)
#     oled.HZ16(48,0,13)
#     time.sleep(5)
# 
