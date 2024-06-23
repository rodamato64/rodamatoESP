#   Rutina REL LG para Casiba-Controller V13.

from machine import reset, Pin, SPI, TouchPad,I2C,SoftI2C,RTC
import ubinascii
from time import sleep
import machine
import os
import gc
gc.collect()

ledLG = Pin(4, Pin.OUT)
LedPrueba = Pin(2, Pin.OUT)
estadoLG = "Apagado"
 
def relLG():
    global estadoLG
    ledLG.value(not ledLG.value())            
    if ledLG.value() == 1:   #   Si el PinTouch27 es tocado, enciende iluminacion LG.
        print("Engine LG ON")
        LedPrueba.value(ledLG.value())
        estadoLG = "Prendido"                    
        sleep(1)
        gc.collect()
        
    else:
        print("Engine LG OFF")    # Establece apagado de LG.
        LG = "OFF"
        LedPrueba.value(ledLG.value())
        ledLG.value(0)
        estadoLG = "Apagado"    
        sleep(1)
        gc.collect()
