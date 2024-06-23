from machine import reset, Pin, SPI, TouchPad,I2C,SoftI2C,RTC
import st7789
import ubinascii
import vga1_bold_16x32 as font1
import vga1_16x16 as font2
import vga1_16x32 as font3
from network import WLAN, AP_IF
import usocket as socket
from time import sleep
from uselect import select
import uasyncio as asyncio
from uasyncio import sleep_ms
import json
import machine
import os
import network
import MOTOR1
import MOTOR2
import RELLG
import RELIL
from MOTOR1 import estadomotor1
from MOTOR2 import estadomotor2
from RELLG import estadoLG
from RELIL import estadoIL
import ds1307
import at24c32n
import utime
import gc
gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

#import micropython
#micropython.mem_info(1)

# ------------------------------------------------------------------
i2c = SoftI2C (scl=Pin(22), sda=Pin(21), freq=400000)
reloj = ds1307.DS1307(i2c)
eeprom = at24c32n.AT24C32N(i2c)

RTC = RTC()
RTC.datetime()
tiempo = RTC.datetime()

##------------- VARIABLES -------------------------------

imagenAncho = 200
imagenAlto = 57
capacitiveValue = 300
threshold = 300 # Threshold to be adjusted (300 funciona)

TP32 = TouchPad(Pin(32))  # TouchPad perteneciente al MOTOR1.
TP33 = TouchPad(Pin(33))  # TouchPad perteneciente al Motor2.
TP27 = TouchPad(Pin(27))  # TouchPad perteneciente al relé LG. 
TP14 = TouchPad(Pin(14))  # TouchPad perteneciente al relé IL.
TP12 = TouchPad(Pin(12))  # TouchPad perteneciente a la habilitación de Display.

ledmotor1 = Pin(13, Pin.OUT)  # Salida al MOTOR 1 y al led de Motor 1 !
ledmotor2 = Pin(16, Pin.OUT)  # Salida al Motor 2 y al led Motor 2.
ledLG = Pin(4, Pin.OUT)   # Salida al relé LG y al led LG.
ledIL = Pin(0, Pin.OUT)   # Salida al relé IL y al led IL.

ledmotor1.value(0)
ledmotor2.value(0)
ledLG.value(0)
ledIL.value(0)

LedPrueba = Pin(2, Pin.OUT)
LedPrueba.value(0)

canthorasM1 = 0
canthorasM2 = 0
canthorasLG = 0
canthorasIL = 0

M1 = 0
M2 = 0
LG = 0
IL = 0

global horahoy
global fechahoy

fechahoy = (str(RTC.datetime()[2])+"/"+str(RTC.datetime()[1])+"/"+str(RTC.datetime()[0]))
print(fechahoy)
horahoy = str(RTC.datetime()[4])+":"+str(RTC.datetime()[5])
print(fechahoy)
print(horahoy)

fecha_inicialM1 = ()
fecha_finalM1 = ()

fecha_inicialM2 = ()
fecha_finalM2 = ()

fecha_inicialLG = ()
fecha_finalLG = ()

fecha_inicialIL = ()
fecha_finalIL = ()

# --------- Calculo de las horas y minutos en base a dos fechas (inicial y final) ---------------

def es_bisiesto(anio):
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)
def convertir_a_segundos(fecha):
    anio, mes, dia, dia_semana, hora, minuto, segundo, decimas = fecha
    # Calcular los días transcurridos desde el año 2000 hasta el año dado
    dias = 0
    for a in range(2000, anio):
        dias += 366 if es_bisiesto(a) else 365
    # Días transcurridos en el año actual hasta el mes dado
    dias_por_mes = [31, 29 if es_bisiesto(anio) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    dias += sum(dias_por_mes[:mes - 1])
    # Añadir los días del mes actual
    dias += dia - 1
    # Convertir todo a segundos
    segundos = dias * 86400 + hora * 3600 + minuto * 60 + segundo
    return segundos
def diferencia_entre_fechas(fecha_inicial, fecha_final):
    segundos_inicial = convertir_a_segundos(fecha_inicial)
    segundos_final = convertir_a_segundos(fecha_final)
    diferencia_segundos = segundos_final - segundos_inicial
    if diferencia_segundos < 0:
        return "Error: La fecha final es anterior a la fecha inicial"
    diferencia_horas = diferencia_segundos // 3600
    diferencia_minutos = (diferencia_segundos % 3600) // 60
    return diferencia_horas, diferencia_minutos

# Ejemplo de uso:
#fecha_inicial = (2023, 6, 12, 1, 8, 30, 0, 0)
#fecha_final = (2023, 6, 13, 2, 10, 45, 0, 0)
#horas, minutos = diferencia_entre_fechas(fecha_inicial, fecha_final)

# -------------------------------------------------------------------------------------------

# Inicialización del Display ST7789 -- Color-1,3"-240x240-TFT 
tft = st7789.ST7789(              
                    SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(23)),
                    240,
                    240,
                    reset=Pin(5, Pin.OUT),
                    dc=Pin(15, Pin.OUT),
                    rotation=0)
tft.init()

# ---------- FUNCIONES / PROGRAMA PRINCIPAL ---------------------------


async def run_engine_1_task():  # Funcion touch (TP32) y activacion Motor 1.
    global fecha_inicialM1
    sleep(0.2)
    while True:
        await sleep_ms(1)
        capacitiveValue = TP32.read()       
        if capacitiveValue < threshold:    # Lee si el PinTouch 32 está tocado ?
            
            MOTOR1.motor1()            #  <--------- SE LLAMA AL MODULO MOTOR1 !!!
            fecha_inicialM1 = RTC.datetime()
                                                          
async def run_engine_2_task():        # Función Touch y activación Motor 2
    global fecha_inicialM2
    sleep(0.2)
    while True:
        await sleep_ms(1)    
        capacitiveValue = TP33.read()
        if capacitiveValue < threshold:   #  Lee si el PinTouch 33 si está tocado.
            MOTOR2.motor2()            # <--------- SE LLAMA AL MODULO MOTOR2 !!!
            fecha_inicialM2 = RTC.datetime()
                                                           
async def run_LG_task():          # Función Touch y activación LG
    global fecha_inicialLG
    sleep(0.2)
    while True:
        await sleep_ms(1)        
        capacitiveValue = TP27.read()      
        if capacitiveValue < threshold:   #  Lee el Pintouch 27 si está tocado.
            RELLG.relLG()           #   <---------- SE LLAMA AL MODULO RELLG !!!
            fecha_inicialLG = RTC.datetime()
                                       
async def run_IL_task():           # Función Touch y activación IL
    global fecha_inicialIL
    sleep(0.2)
    while True:
        await sleep_ms(1)       
        capacitiveValue = TP14.read()
        if capacitiveValue < threshold:   # Lee el Pintouch 14 si está tocado.
            RELIL.relIL()       #  <------------ SE LLAMA AL MODULO RELIL !!!
            fecha_inicialIL = RTC.datetime()

def send_response(conn):    # "Pagina Web HTML"
    global fechahoy,horahoy
    canthorasM1 = eeprom.read(0,10).decode("utf-8")
    canthorasM2 = eeprom.read(10,10).decode("utf-8")
    canthorasLG = eeprom.read(20,10).decode("utf-8")
    canthorasIL = eeprom.read(30,10).decode("utf-8")
    from MOTOR1 import estadomotor1
    from MOTOR2 import estadomotor2
    from RELLG import estadoLG
    from RELIL import estadoIL
    
    try:
        response = 'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\nConnection:close\r\n\r\n'
        response += (
        """
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="data:,">
        <style>
        html{font-family: cambria italic; display:inline-block; margin: 0px auto; text-align: center;}
        h1{color: #0F3376; font-size: 3rem;font-style:italic;}
        p{font-size: 1.5rem;color:#0F3376;}
        h2{font-size: 2rem;text-decoration:underline;}
        </style>
        </head>
        
        <body>
        <meta http-equiv="refresh" content="3">
        <h1>  CASIBA  </h1>
        <p>("""+ fechahoy +""" - - - """+ horahoy +""")</p> 
        <p><strong>FILTRACION DE AIRE</strong></p>
        <h2>Estado de Salidas:</h2>    
        <p>Estado Motor 1: <strong>"""
            + estadomotor1
            + """</strong></p>
        <p style="color:green">Cant.Horas Motor 1: <strong>"""
            + canthorasM1
            + """</strong></p>
        <p></p>
        <p>Estado Motor 2: <strong>"""
            + estadomotor2
            + """</strong></p>
        <p style="color:red">Cant.Horas Motor 2: <strong>"""
            + canthorasM2
            + """</strong></p>
        <p>Estado LG: <strong>"""
            + estadoLG
            + """</strong></p>
        <p style="color: blue">Cant.Horas LG: <strong>"""
            + canthorasLG
            + """</strong></p>
        <p>Estado IL: <strong>"""
            + estadoIL
            + """</strong></p>
        <p style= "color:magenta">Cant.Horas IL: <strong>"""
            + canthorasIL
            + """</strong></p>
        </body>
        </html>\r\n"""
        )

        gc.collect()
        conn.sendall(response)
    except Exception as exc:       
        print("Send Response Err", exc.args[0])
        pass
    finally:
        conn.close()
        gc.collect()
      
async def run_socket():  # Función activación SOCKET
    print("Paso por run_socket")
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 80))
        s.listen(5)
        print("HTTP server ready on port 80")
    except Exception as exc:
        print("Address in use, restarting", exc.args[0])
        sleep(5)
        reset()
        pass
    while True:
        r, w, err = select((s,), (), (), 0)
        if r:
            for readable in r:
                conn, _ = s.accept()
                conn.settimeout(1)
                print('Incoming request', conn)
                send_response(conn)
                await sleep_ms(1)
        await sleep_ms(1)
        gc.collect()

async def activeDisplay():   #  Función de activación de secuencia de Display.
    global fechahoy,horahoy
    sleep(0.2)
    while True:
        await sleep_ms(1) 
        capacitivevalue = TP12.read() 
        if capacitivevalue < threshold:   #  Lee si el Pintouch 12 está tocado.
            
            file = open("LC200x57.raw", "rb")
            buf = file.read()
            file.close()
            tft.text(font1, fechahoy, 50, 16,st7789.WHITE, st7789.BLACK)
            tft.text(font1, horahoy, 80, 56,st7789.WHITE, st7789.BLACK)
            tft.blit_buffer(buf, 16, 110, imagenAncho, imagenAlto)
            gc.collect()
       
            sleep(2.5)
            LedPrueba.value(not LedPrueba.value())
         
            from MOTOR1 import estadomotor1
            canthorasM1 = eeprom.read(0,10).decode("utf-8")
            tft.fill(st7789.GREEN)
            tft.text(font1, "MOTOR 1:", 40, 26, st7789.BLACK,st7789.WHITE)
            tft.text(font1, estadomotor1, 40, 66,st7789.BLACK, st7789.WHITE)
            tft.text(font1, "Cant.horas:", 26, 126, st7789.BLACK,st7789.WHITE)
            tft.text(font1, canthorasM1, 70, 166, st7789.BLACK,st7789.WHITE)
            gc.collect() 
            sleep(2)
            LedPrueba.value(not LedPrueba.value())
            
            from MOTOR2 import estadomotor2
            canthorasM2 = eeprom.read(10,10).decode("utf-8")
            tft.fill(st7789.RED)
            tft.text(font1, "MOTOR 2:", 40, 26,st7789.BLACK,st7789.WHITE)
            tft.text(font1, estadomotor2, 40, 66,st7789.BLACK, st7789.WHITE)
            tft.text(font1, "Cant.horas:", 26, 126, st7789.BLACK,st7789.WHITE)
            tft.text(font1, canthorasM2, 70, 166, st7789.BLACK,st7789.WHITE)
            gc.collect() 
            sleep(2)
            LedPrueba.value(not LedPrueba.value())
            
            from RELLG import estadoLG
            canthorasLG = eeprom.read(20,10).decode("utf-8")
            tft.fill(st7789.BLUE)
            tft.text(font1, "LG :", 60, 26,st7789.BLACK,st7789.WHITE)
            tft.text(font1, estadoLG, 40, 66,st7789.BLACK, st7789.WHITE)
            tft.text(font1, "Cant.horas:", 35, 126, st7789.BLACK, st7789.WHITE)
            tft.text(font1, canthorasLG, 70, 166, st7789.BLACK, st7789.WHITE)
            gc.collect()  
            sleep(2)
            LedPrueba.value(not LedPrueba.value())
            
            from RELIL import estadoIL
            canthorasIL = eeprom.read(30,10).decode("utf-8")
            tft.fill(st7789.MAGENTA)
            tft.text(font1, "IL : ", 60, 26,st7789.BLACK,st7789.WHITE)
            tft.text(font1, estadoIL, 40, 66,st7789.BLACK, st7789.WHITE)
            tft.text(font1, "Cant.horas:", 35, 126, st7789.BLACK,st7789.WHITE)
            tft.text(font1, canthorasIL, 70, 166, st7789.BLACK,st7789.WHITE)
            gc.collect()
            sleep(2)
            
            tft.fill(st7789.BLACK)
            LedPrueba.off()


def create_ap_connection():        ######  ESTABLECE CONEXION WIFI !!!
    ssid = "CasibaEngineController"
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid)
    while ap.active() == False:
       pass
    print(f"AP {ssid} ready on {ap.ifconfig()[0]}")
    gc.collect()

async def Timer():
    global M1,M2,LG,IL,fecha_inicialM1,fecha_inicialM2,fecha_inicialLG,fecha_inicialIL
    while True:
        await sleep_ms(1) 
        sleep(0.2)
        if ledmotor1.value() == 1:
            M1 = M1 + 1
            if M1 == 17000:                      # 17000 es equivalente a 50 minutos.
                M1 = 0
                fecha_finalM1 = RTC.datetime()
                sleep(0.1)
                fecha_inicial = fecha_inicialM1
                fecha_final = fecha_finalM1
                horas, minutos = diferencia_entre_fechas(fecha_inicial, fecha_final)
                print("horas : "+str(horas))
                print("minutos : "+str(minutos))
                horasM1sumadas = int(eeprom.read(0,10).decode("utf-8")) + horas
                sleep(0.1)
                eeprom.write(0,str(horasM1sumadas))
                sleep(0.1)
                          
        if ledmotor2.value() == 1:
            M2 = M2 + 1
            if M2 == 17000:                      # 17000 es equivalente a 50 minutos.
                M2 = 0
                fecha_finalM2 = RTC.datetime()
                sleep(0.1)
                fecha_inicial = fecha_inicialM2
                fecha_final = fecha_finalM2
                horas, minutos = diferencia_entre_fechas(fecha_inicial, fecha_final)
                print("horas : "+str(horas))
                print("minutos : "+str(minutos))
                horasM2sumadas = int(eeprom.read(10,10).decode("utf-8")) + horas
                sleep(0.1)
                eeprom.write(10,str(horasM2sumadas))
                sleep(0.1)
                              
        if ledLG.value() == 1:
            LG = LG + 1
            if LG == 17000:
                LG = 0
                fecha_finalLG = RTC.datetime()
                sleep(0.1)
                fecha_inicial = fecha_inicialLG
                fecha_final = fecha_finalLG
                horas, minutos = diferencia_entre_fechas(fecha_inicial, fecha_final)
                print("horas : "+str(horas))
                print("minutos : "+str(minutos))
                horasLGsumadas = int(eeprom.read(20,10).decode("utf-8")) + horas
                sleep(0.1)
                eeprom.write(20,str(horasLGsumadas))
                sleep(0.1)
                             
        if ledIL.value() == 1:
            IL = IL + 1
            if IL == 17000:
                IL = 0
                fecha_finalIL = RTC.datetime()
                sleep(0.1)
                fecha_inicial = fecha_inicialIL
                fecha_final = fecha_finalIL
                horas, minutos = diferencia_entre_fechas(fecha_inicial, fecha_final)
                print("horas : "+str(horas))
                print("minutos : "+str(minutos))
                horasILsumadas = int(eeprom.read(30,10).decode("utf-8")) + horas
                sleep(0.1)
                eeprom.write(30,str(horasILsumadas))
                sleep(0.1)
                
                    
# --------- Se llaman las funciones sincrónicas(secuenciales) y asincrónicas (ASYNC) ------------


create_ap_connection()
loop = asyncio.get_event_loop()
loop.create_task(run_socket())
loop.create_task(run_engine_1_task())
loop.create_task(run_engine_2_task())
loop.create_task(run_LG_task())
loop.create_task(run_IL_task())
loop.create_task(activeDisplay())
loop.create_task(Timer())
loop.run_forever()



    

  