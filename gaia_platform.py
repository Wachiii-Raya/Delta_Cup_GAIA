from typing_extensions import Self
import serial
import struct
import mysql.connector
import Gaia_variable
import multiprocessing as mp
#import pandas as pd

# Initialize a variable
port = 'COM3', baudrate = 9600
gv = Gaia_variable()

#read sensor value from csv.
# data = pd.read_csv('Path') # fill later

db = mysql.connector.connect(
    host="localhost",  #127.0.0.1
    user="root",
    password="delta_gaia",
    database="Delta_Gaia"
)
mycursor = db.cursor()

# Input from serial.read
ser = serial.Serial(port=port, baudrate=baudrate)

# def read_sensor():
while True:
    cc = bytearray(ser.readline())
    if len(cc) == 113:
        sensors_list = list(struct.unpack('<ffh', cc))[2:-1]
        mycursor.execute(f"UPDATE sensors_status SET value = sensors_list[0], valve_id = 1")
        mycursor.execute(f"UPDATE sensors_status SET value = sensors_list[1], valve_id = 2")
        db.commit()
    feature_list = gv.create_features_list(sensors_list)

def all_process():
    while feature_list[0] not in range(6.0,8.0):    
        gv.check_pH(feature)
    mycursor.execute(f"UPDATE sensors_status SET value = sensors_list[0], valve_id = 1")
    mycursor.execute(f"UPDATE valves_status SET status = valves_list[0], valve_id = 1")
    mycursor.execute(f"UPDATE valves_status SET status = valves_list[1], valve_id = 2")
    db.commit()
    gv

    





