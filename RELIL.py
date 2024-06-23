#   Rutina REL IL para Casiba controller V13. 

from machine import reset, Pin, SPI, TouchPad,I2C,SoftI2C,RTC
import ubinascii
from time import sleep
import machine
import os
import gc
gc.collect()

ledIL = Pin(0, Pin.OUT)
LedPrueba = Pin(2, Pin.OUT)
estadoIL = "Apagado"
   
def relIL():
    global estadoIL
    ledIL.value(not ledIL.value())
    if ledIL.value() == 1:   # Si el PinTouch14 está tocado, enciende IL.
        print(" IL ON")
        LedPrueba.value(ledIL.value())
        estadoIL = "Prendido" 
        sleep(1)
        gc.collect()
        
    else:
        print(" IL OFF")       # establece el apagado de IL.
        LedPrueba.value(ledIL.value())
        ledIL.value(0)
        estadoIL = "Apagado"
        sleep(1)
        gc.collect()



 
 
 
 
 
 
 
 
 
 
 
 
 
 
    