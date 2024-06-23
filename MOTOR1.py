#  Rutina Motor 1 para Casiba controller V13.

from machine import reset, Pin, SPI, TouchPad,I2C,SoftI2C,RTC
import ubinascii
from time import sleep
import machine
import os
import gc
gc.collect()


ledmotor1 = Pin(13, Pin.OUT)
LedPrueba = Pin(2, Pin.OUT)
estadomotor1 = "Apagado"


def motor1():
    global estadomotor1,canthorasM1
    ledmotor1.value(not ledmotor1.value())
    print(ledmotor1.value())
    if ledmotor1.value() == 1:  #  Si está tocado, prende motor1 y ledmotor1
        LedPrueba.value(ledmotor1.value()) 
        print("Engine 1 ON")             
        estadomotor1 = "Prendido"
        sleep(1)
        gc.collect()
                                                       
    else:
        print("Engine 1 OFF")  # Establece apagado motor M1                
        LedPrueba.value(ledmotor1.value())
        ledmotor1.value(0)                  
        estadomotor1 = "Apagado"        
        sleep(1)
        gc.collect()



