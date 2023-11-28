import serial
import struct
import mysql.connector
from Gaia_variable import Gaia101

import time
# import multiprocessing
# import threading

# baudrate = 9600
# ser = serial.Serial(port='COM5', baudrate=baudrate)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="delta_gaia",
    database="gaia_properties"
)
gv = Gaia101()
mycursor = db.cursor(buffered=True)

# Create Database for mysql server named as Bioreactor //if needed
mycursor.execute("CREATE DATABASE IF NOT EXISTS Gaia_properties")
mycursor.execute("USE Gaia_properties")

# Create sensor table //sensor1 = pH, sensor2 = tempt
mycursor.execute("CREATE TABLE IF NOT EXISTS sensor_list (id int PRIMARY KEY AUTO_INCREMENT, pH_sensor FLOAT NOT NULL, tempt_sensor FLOAT NOT NULL)")
mycursor.execute("DESCRIBE sensor_list")

# Create valve table
# valve1 = base buffer, valve2 = acid buffer, valve3 = NaCO
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS valve (id int PRIMARY KEY AUTO_INCREMENT, base_buffer BOOLEAN NOT NULL, acid_buffer BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE valve")

# Create motor table
# motor1 = media, motor2 = cell, motor3= agitator, motor4 = bioreactor, motor5 = tube_rotator1, motor6 = centrifuge, motor7 = tube_rotator_2
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS motor (id int PRIMARY KEY AUTO_INCREMENT, media BOOLEAN NOT NULL, cell BOOLEAN NOT NULL, agitator BOOLEAN NOT NULL, bioreactor BOOLEAN NOT NULL, "
    "tube_rotator1 int NOT NULL, centrifuge BOOLEAN NOT NULL, tube_rotator2 int NOT NULL, NaClO BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE motor")

mycursor.execute("CREATE TABLE IF NOT EXISTS six_axis_command (id int PRIMARY KEY AUTO_INCREMENT, Func_1 BOOLEAN NOT NULL, Func_2 BOOLEAN NOT NULL, Func_3 BOOLEAN NOT NULL, "
                 "Func_4 BOOLEAN NOT NULL, Func_5 BOOLEAN NOT NULL, Func_6 BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE six_axis_command")

mycursor.execute("CREATE TABLE IF NOT EXISTS six_axis_feedback (id int PRIMARY KEY AUTO_INCREMENT, Func_1 BOOLEAN NOT NULL, Func_2 BOOLEAN NOT NULL, Func_3 BOOLEAN NOT NULL, "
                 "Func_4 BOOLEAN NOT NULL, Func_5 BOOLEAN NOT NULL, Func_6 BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE six_axis_feedback")
db.commit()

[mycursor.execute(f"SELECT * FROM sensor_list")]
[mycursor.execute(f"SELECT * FROM valve")]
[mycursor.execute(f"SELECT * FROM motor")]
[mycursor.execute(f"INSERT INTO sensor_list(pH_sensor,tempt_sensor) VALUES (0,0)")]
[mycursor.execute(f"INSERT INTO valve(base_buffer, acid_buffer) VALUES (0,0)")]
[mycursor.execute(f"INSERT INTO motor(media, cell, agitator, bioreactor, tube_rotator1, centrifuge, tube_rotator2, NaClO) VALUES (0,0,0,0,0,0,0,0)")]
[mycursor.execute(f"INSERT INTO six_axis_command(Func_1, Func_2, Func_3, Func_4, Func_5, Func_6) VALUES (0,0,0,0,0,0)")]
[mycursor.execute(f"INSERT INTO six_axis_feedback(Func_1, Func_2, Func_3, Func_4, Func_5, Func_6) VALUES (0,0,0,0,0,0)")]
db.commit()


pH = 7
temp = 31
gv.sensor_list[0] = pH
gv.sensor_list[1] = temp


# def ArduinoRead():
#     # Read data from arduino UNO
#     # not sure chfff smth
#     # **python arduino struct read: https://stackoverflow.com/questions/60306952/how-to-read-a-data-struct-sent-serially-from-an-arduino
#     while True:
#         cc = bytearray(ser.readline())
#         if len(cc) == 10:  # package variable ที่จะส่งมาจาก arduino # not sure number of the board
#             sensor_list = list(struct.unpack('ffh', cc))[:]  # returned as elements of tuple
#             pH = round(sensor_list[0], 5)
#             temp = round(sensor_list[1], 3)
#             [mycursor.execute(f"UPDATE sensor_list SET pH_sensor = '{pH}' WHERE id = '1'")]
#             [mycursor.execute(f"UPDATE sensor_list SET temp_sensor = {temp} WHERE id = '1'")]
#             db.commit()
#             features_list = gv.create_features_list(sensors_list)

def write_read(data):
    print(data)
    # ser.write(bytes(data, 'utf-8'))
    return data

def sendtoArduino():
    if gv.motor[1] == 1: #cell
        write_read("9")
    elif gv.motor[3] == 1: #bioreact
        write_read("10")
    elif gv.motor[7] == 1: #NaClO
        write_read("11")

def pump_to_tube():
    for pos in range(1, 13):  # round 1 pos = 1-2 wait for placing
        pos_around = (pos)*(-625)
        # add bioreactor to tube
        time.sleep(2)
        gv.motor_on(3)
        sendtoArduino()
        [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor[3]} WHERE id = '1'")]
        db.commit()
        time.sleep(2)
        print("bio")
        gv.motor_off(3)
        time.sleep(2)
        write_read("5")
        [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor[3]} WHERE id = '1'")]
        db.commit()

        # rotate tube_rotator1
        gv.motor_on(4)
        print(pos_around)
        [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {pos_around} WHERE id = '1'")]
        db.commit()
        time.sleep(10)
        print("r1")
        gv.motor_off(4)
        #[mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor[4]} WHERE id = '1'")]
        #db.commit()

        # (6-axis) move tube to centrifuge process @take_tube position from tube_rotator1 #DI1
        [mycursor.execute(f"UPDATE six_axis_command SET Func_1 = '1' WHERE id = '1'")]  # DI1
        db.commit()
        time.sleep(35)  # time delay ตอนรอ 6-axis ขยับ
        print("func1")
        [mycursor.execute(f"UPDATE six_axis_command SET Func_1 = '0' WHERE id = '1'")]  # DI2
        db.commit()

        while (True):  # pick from cen + place on rotator
            time.sleep(5)
            [mycursor.execute(f"SELECT Func_1 FROM six_axis_feedback WHERE id = '1'")]
            six_axis = mycursor.fetchone()
            if six_axis[0] == 0 : break

        # rotate centrifuge for 1 position....
        gv.motor_on(5)
        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
        db.commit()
        time.sleep(5)
        print("cen_ro")
        gv.motor_off(5)
        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
        db.commit()

        if pos % 6 ==0 :  # centrifuge process for 5 mins or else? /not sure the time yet
            # centrifuge roundx.1
            gv.motor_on(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
            time.sleep(400) # cen time ???!!
            print("cen")
            gv.motor_off(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()

            for r2 in range(6):
                if pos == 6 : sean = (r2+1)*(-625)
                elif pos ==12 : sean = (r2 + 7) * (-625)
                [mycursor.execute(f"UPDATE six_axis_command SET Func_3 = 1 WHERE id = '1'")]  # DI3
                db.commit()
                time.sleep(50)  # time delay ตอนรอ 6-axis ขยับ
                print("func3")
                [mycursor.execute(f"UPDATE six_axis_command SET Func_3 = 0 WHERE id = '1'")]  # DI3
                db.commit()
                while (True):  # pick from cen + place on rotator2 #DI3
                    time.sleep(2)
                    [mycursor.execute(f"SELECT Func_3 FROM six_axis_feedback WHERE id = '1'")]
                    six_axis = mycursor.fetchone()
                    if six_axis[0] == 0 : break
                # rotate tube_rotator2
                gv.motor_on(6)
                print(sean)
                [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {sean} WHERE id = '1'")]
                db.commit()
                time.sleep(10)
                print("r2")
                gv.motor_off(6)
                #[mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                db.commit()

                # add NaClO into tube
                time.sleep(2)
                gv.motor_on(7)
                sendtoArduino()
                [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor[7]} WHERE id = '1'")]
                db.commit()
                time.sleep(2)
                print("NaClO")
                gv.motor_off(7)
                time.sleep(2)
                write_read("6")
                [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor[7]} WHERE id = '1'")]
                db.commit()



    for pos_cen in range(1, 13):
        # rotate tube_rotator2
        # (6-axis) move tube from tube_rotator2 @take_tube position to centrifuge
        time.sleep(3600)

        [mycursor.execute(f"UPDATE six_axis_command SET Func_4 = 1 WHERE id = '1'")]  # DI4
        db.commit()
        time.sleep(35)
        print("func4")
        [mycursor.execute(f"UPDATE six_axis_command SET Func_4 = 0 WHERE id = '1'")]  # DI4
        db.commit()
        while (True):  # pick from cen + place on rotator
            time.sleep(2)
            [mycursor.execute(f"SELECT Func_4 FROM six_axis_feedback WHERE id = '1'")]
            six_axis = mycursor.fetchone()
            if six_axis[0] == 0: break

        gv.motor_on(5)
        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
        db.commit()
        time.sleep(5)
        print("cen_ro")
        gv.motor_off(5)
        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
        db.commit()

        jean = (pos_cen + 12) * (-625)
        print(jean)
        gv.motor_on(6)
        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {jean} WHERE id = '1'")]
        db.commit()
        time.sleep(2)
        print("r2")
        gv.motor_off(6)
        # [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
        # db.commit()
        # ใช้ฟังชั่นสองตัวแบบนี้ไม่ได้เนื่องจากเวลาในการไปแต่ละตำแหน่งแรคไม่เท่ากัน ต้องแยกกรณี 12 หลุมเลออออ
        if pos_cen == 6:  # pos12==func6
            gv.motor_on(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
            time.sleep(400) #cen time ???!!!
            print("cen")
            gv.motor_off(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()

            for cen_rotate in range(6):
                [mycursor.execute(f"UPDATE six_axis_command SET Func_5 = 1 WHERE id = '1'")]  # DI5
                db.commit()
                time.sleep(50)
                print("func5")
                [mycursor.execute(f"UPDATE six_axis_command SET Func_5 = 0 WHERE id = '1'")]  # DI5
                db.commit()
                while (True):  # pick from cen + place on rotator
                    time.sleep(2)
                    [mycursor.execute(f"SELECT Func_5 FROM six_axis_feedback WHERE id = '1'")]
                    six_axis = mycursor.fetchone()
                    if six_axis[0] == 0 : break

                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(5)
                print("cen_ro")
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

        elif pos_cen == 12:  # pos12==func6
            gv.motor_on(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
            time.sleep(400) # cen time ???!!
            print("cen")
            gv.motor_off(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()

            for cen_rotate in range(6):
                [mycursor.execute(f"UPDATE six_axis_command SET Func_6 = 1 WHERE id = '1'")]  # DI5
                db.commit()
                time.sleep(50)
                print("func6")
                [mycursor.execute(f"UPDATE six_axis_command SET Func_6 = 0 WHERE id = '1'")]  # DI5
                db.commit()
                while (True):  # pick from cen + place on rotator
                    time.sleep(2)
                    [mycursor.execute(f"SELECT Func_6 FROM six_axis_feedback WHERE id = '1'")]
                    six_axis = mycursor.fetchone()
                    if six_axis[0] == 0 : break

                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(5)
                print("cen_ro")
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()


if __name__ == '__main__':
    pump_to_tube()



