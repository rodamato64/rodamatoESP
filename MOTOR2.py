#   Rutina Motor 2 para Casiba controller V13.
from machine import reset, Pin, SPI, TouchPad,I2C,SoftI2C,RTC
import ubinascii
from time import sleep
import json
import machine
import os
import gc
gc.collect()

ledmotor2 = Pin(16, Pin.OUT)
LedPrueba = Pin(2, Pin.OUT)
estadomotor2 = "Apagado"
   
def motor2():
    global estadomotor2
    ledmotor2.value(not ledmotor2.value()) 
    print(ledmotor2.value())
    if ledmotor2.value() == 1:  #  Si el PinTouch33 es tocado, enciende motor M2 y ledmotor M2. 
        print("Engine 2 ON")
        LedPrueba.value(ledmotor2.value())                           
        estadomotor2 = "Prendido"                
        sleep(1)
                                                        
    else:
        print("Engine 2 OFF")    # Establece apagado del motor M2
        LedPrueba.value(ledmotor2.value())
        ledmotor2.value(0)
        estadomotor2 = "Apagado"
        sleep(1)
        gc.collect()    









