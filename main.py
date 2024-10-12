from misc.update import pip
import sys
import subprocess
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

clear()
pip("yollor")
pip("pyfirmata")
pip("requests")
pip("streamlit")
pip("panda")
clear()

from yollor import *
from pyfirmata import Arduino, util
from time import sleep
import requests
from datetime import datetime
import sqlite3 # Possivelmente vou ter q clcr algum sistema web para vizualização avançada dessa db
from misc import port

DBConnecting = sqlite3.connect("./misc/DB_Projeto01.db")
DBCursor = DBConnecting.cursor()

DBCursor.execute('''
CREATE TABLE IF NOT EXISTS RegistrosEstufa (
                 id INTEGER PRIMARY KEY,
                 horadata TEXT NOT NULL,
                 umidade INT NOT NULL,
                 luminosidade INT NOT NULL
)
''')

porta = port.get_arduino_port()
print("Identificando Porta")
sleep(2)
print(f"Porta identificada: {porta}")

port = porta 

if port is None:
    raise IOError("Nenhuma placa Arduino encontrada.")

print(f"Conectando na porta {port}")
board = Arduino(port)

AnalogicPins = util.Iterator(board)
AnalogicPins.start() 

# Lendo o pino a0
LDR_pin = board.get_pin('a:0:i')
dampPIN = board.get_pin('a:1:i')

def GetTime(mode):
    response = requests.get('https://worldtimeapi.org/api/timezone/America/Sao_Paulo')
    data = response.json()

    DatetimeSTR = data['datetime']
    TimeSTR = DatetimeSTR.split('T')[1].split('.')[0]
    DateSTR = DatetimeSTR.split('T')[0]

    if mode == 'data':
        return DateSTR
    if mode == 'hora':
        return TimeSTR
    if mode == 'all':
        return f"{DateSTR} {TimeSTR}"


def GetLightLevel():
    sleep(3)
    LDR_output = LDR_pin.read()
    return LDR_output

def GetDampLevel():
    sleep(3)
    damp_output = dampPIN.read()
    return damp_output
    
def NewLogLine(content, filename): 
    time = GetTime('hora')
    NewContent = f"{content} | {time}"
    with open(filename, 'a') as file:
        file.write(NewContent + '\n')
    
    print(f"Log registrado: {content}")

class LedComp:
    relay_pin = board.get_pin('d:9:o') 

    #abaixo deixo dias de choro suor e sangue
    #pior implementação possivel mas funciona e isso que importa 

    @staticmethod
    def TurnOn():
        LedComp.relay_pin.write(1) 
        print(f"{c.green('LED USB ON')}") 
        NewLogLine(content="LED USB ON", filename="./misc/LogMonitoramento_Projeto01.txt") 

    @staticmethod
    def TurnOff():
        LedComp.relay_pin.write(0) 
        print(f"{c.red('LED USB OFF')}") 
        NewLogLine(content="LED USB OFF", filename="./misc/LogMonitoramento_Projeto01.txt") 

def DampConv(resistance):
    min_resistance = 0.0  # Res. Min. Sensor seco
    max_resistance = 1.0  # Res. Max. Sensor completamente imerso em água
    
    humidity = 100 - ((resistance - min_resistance) / (max_resistance - min_resistance) * 100)
    
    return max(0, min(100, humidity))

def LumConv(resistance):
    min_resistance = 1.0  # escuridão total
    max_resistance = 0.1  # luz intensa
    
    if resistance <= 0:
        return 0 
    lumens = (max_resistance / resistance) * 1000  
    
    return lumens

def db_viewer():
    subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', './misc/db_view.py'])  
    sleep(5)
    print("Para visualizar os logs, acesse o link: http://localhost:8501") 

def ConvertTimeToMinutes(time_str):
    hours, minutes, _ = map(int, time_str.split(':'))
    total_minutes = hours * 60 + minutes
    return total_minutes

def main():
    
    NewLogLine("Iniciado protocolo de monitoramento.", "./misc/LogMonitoramento_Projeto01.txt")
    sleep(1.4)
    sleep(1.6)
    db_viewer()
    NewLogLine("Database Hosting iniciada", "./misc/LogMonitoramento_Projeto01.txt")

    while True:

        HoraHora = GetTime('hora')
        HoraMinutos = int(ConvertTimeToMinutes(str(HoraHora)))

        if HoraMinutos > 360 and HoraMinutos < 540:    # Entre 6 e 9 da manhã
            LedComp.TurnOn()
            pass
        elif HoraMinutos > 540 and HoraMinutos < 660:  # Das 9 as 11
            LedComp.TurnOff()
            pass
        elif HoraMinutos > 660 and HoraMinutos < 840:  # Entre 11 e 14hrs
            LedComp.TurnOn()
            pass
        elif HoraMinutos > 840 and HoraMinutos < 960:  # Das 14 as 16
            LedComp.TurnOff()
            pass
        elif HoraMinutos > 960 and HoraMinutos < 1140: # 16hrs até as 19
            LedComp.TurnOn()
            pass
        elif HoraMinutos > 1140 and HoraMinutos < 360: # Tempo desligado (19-06hrs)
            LedComp.TurnOff()
            pass

        DateTime = GetTime('all')
        damp = DampConv(GetDampLevel())
        luminosidade = LumConv(GetLightLevel())
        DBCursor.execute('''
INSERT INTO RegistrosEstufa (horadata, umidade, luminosidade) VALUES (?, ?, ?)
''', (DateTime, damp, luminosidade))
        NewLogLine("Novo registro geral adicionado a database", "./misc/LogMonitoramento_Projeto01.txt")
        DBConnecting.commit()
        sleep(300)
        

if __name__ == "__main__":
    main()