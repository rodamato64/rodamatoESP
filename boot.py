#    boot.py para versión "Casiba Controller V13 "

# This file is executed on every boot (including wake-boot from deepsleep)

#import webrepl
#webrepl.start()
try:
  import usocket as socket
except:
  import socket

import network
import utime as time
import esp
esp.osdebug(None)

import gc
gc.collect()
