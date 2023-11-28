import serial
import mysql.connector
from Gaia_variable import Gaia101
import time
# import multiprocessing  # ยังไม่ได้ใส่คำสั่งนี้

# Initialize a variable
gv = Gaia101()

# connect to database maybe have to connect with the created database in mySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="delta_gaia",
    database="gaia_properties"
)
mycursor = db.cursor(buffered = True)

# Input from serial.read
ser = serial.Serial(port='COM3', baudrate=9600)

# Create Database for mysql server named as Bioreactor //if needed
mycursor.execute("CREATE DATABASE IF NOT EXISTS Gaia_properties")
mycursor.execute("USE gaia_properties")

# Create sensor table //sensor1 = pH, sensor2 = tempt
mycursor.execute("CREATE TABLE IF NOT EXISTS sensor_list (id int PRIMARY KEY AUTO_INCREMENT, pH_sensor FLOAT NOT NULL, tempt_sensor FLOAT NOT NULL)")
mycursor.execute("DESCRIBE sensor_list")

# Create valve table
# valve1 = base buffer, valve2 = acid buffer, valve3 = NaCO
mycursor.execute("CREATE TABLE IF NOT EXISTS valve (id int PRIMARY KEY AUTO_INCREMENT, base_buffer BOOLEAN NOT NULL, acid_buffer BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE valve")

# Create motor table
# motor1 = media, motor2 = cell, motor3= agitator, motor4 = bioreactor, motor5 = tube_rotator1, motor6 = centrifuge, motor7 = tube_rotator_2
mycursor.execute("CREATE TABLE IF NOT EXISTS motor (id int PRIMARY KEY AUTO_INCREMENT, media BOOLEAN NOT NULL, cell BOOLEAN NOT NULL, agitator BOOLEAN NOT NULL, bioreactor BOOLEAN NOT NULL, tube_rotator1 BOOLEAN NOT NULL, centrifuge BOOLEAN NOT NULL, tube_rotator2 BOOLEAN NOT NULL, NaClO BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE motor")

mycursor.execute("CREATE TABLE IF NOT EXISTS 6_axis_command (id int PRIMARY KEY AUTO_INCREMENT, Func_1 BOOLEAN NOT NULL, Func_2 BOOLEAN NOT NULL, Func_3 BOOLEAN NOT NULL, Func_4 BOOLEAN NOT NULL, Func_5 BOOLEAN NOT NULL, Func_6 BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE 6_axis_command")

mycursor.execute("CREATE TABLE IF NOT EXISTS 6_axis_feedback (id int PRIMARY KEY AUTO_INCREMENT, Func_1 BOOLEAN NOT NULL, Func_2 BOOLEAN NOT NULL, Func_3 BOOLEAN NOT NULL, Func_4 BOOLEAN NOT NULL, Func_5 BOOLEAN NOT NULL, Func_6 BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE 6_axis_feedback")

db.commit()

[mycursor.execute(f"SELECT * FROM sensor_list")]
[mycursor.execute(f"SELECT * FROM valve")]
[mycursor.execute(f"SELECT * FROM motor")]
[mycursor.execute(f"INSERT INTO sensor_list(pH_sensor,tempt_sensor) VALUES (0,0)")]
[mycursor.execute(f"INSERT INTO valve(base_buffer, acid_buffer) VALUES (0,0)")]
[mycursor.execute(f"INSERT INTO motor(media, cell, agitator, bioreactor, tube_rotator1, centrifuge, tube_rotator2, NaClO) VALUES (0,0,0,0,0,0,0,0)")]
[mycursor.execute(f"INSERT INTO 6_axis_command(Func_1, Func_2, Func_3, Func_4, Func_5, Func_6) VALUES (0,0,0,0,0,0)")]
[mycursor.execute(f"INSERT INTO 6_axis_feedback(Func_1, Func_2, Func_3, Func_4, Func_5, Func_6) VALUES (0,0,0,0,0,0)")]
db.commit()
# do 2 functions at the same time
#def MultiProcessing():
    # how to;-;
#    print('read dis one: https://linuxhint.com/python-multiprocessing-example/')


def ArduinoRead():
    # Read data from arduino UNO
    # not sure chfff smth
    # **python arduino struct read: https://stackoverflow.com/questions/60306952/how-to-read-a-data-struct-sent-serially-from-an-arduino
    while True:
        cc = bytearray(ser.readline())
        if len(cc) == 10:  # package variable ที่จะส่งมาจาก arduino # not sure number of the board
            sensor_list = list(struct.unpack('ffh', cc))[:]  # returned as elements of tuple
            #sensor_list[0] = 7.2748278
            pH = round(sensor_list[0], 5)
            temp = round(sensor_list[1], 3)
            [mycursor.execute(f"UPDATE sensor_list SET pH_sensor = '{pH}' WHERE id = '1'")]
            [mycursor.execute(f"UPDATE sensor_list SET temp_sensor = {temp} WHERE id = '1'")]
            db.commit()
            features_list = gv.create_features_list(sensors_list)


def Process():
    while gv.motor[0] == 0:
        gv.pHChecker()
        [mycursor.execute(f"UPDATE valve SET base_buffer = {gv.GaiaProperty_dict['valve'][f'valve{1}']} WHERE id = '1'")]
        [mycursor.execute(f"UPDATE valve SET acid_buffer = {gv.GaiaProperty_dict['valve'][f'valve{2}']} WHERE id = '1'")]
        db.commit()
        time.sleep(5)
        [mycursor.execute(f"UPDATE valve SET base_buffer = 0 WHERE id = '1'")]
        [mycursor.execute(f"UPDATE valve SET acid_buffer = 0 WHERE id = '1'")]
        db.commit()
        time.sleep(60)  # รอให้ buffer mix with media แล้วค่อย recheck not sure

def add_media():  # add 80% of 5 L = 4 L
    gv.motor_on(0)
    [mycursor.execute(f"UPDATE motor SET media = {gv.motor[0]} WHERE id = '1'")]
    db.commit()
    time.sleep(t_add_media)
    gv.motor_off(0)
    [mycursor.execute(f"UPDATE motor SET media = {gv.motor[0]} WHERE id = '1'")]
    db.commit()


def add_cell():  # add 20% of 5 L = 1 L
    gv.motor_on(1)
    time.sleep(2)
    gv.sendArduino()
    [mycursor.execute(f"UPDATE motor SET cell = {gv.motor[1]} WHERE id = '1'")]
    db.commit()
    time.sleep(t_add_cell)
    gv.motor_off(1)
    time.sleep(2)
    gv.write_read("4")
    [mycursor.execute(f"UPDATE motor SET cell = {gv.motor[1]} WHERE id = '1'")]
    db.commit()


def agitator():
    gv.motor_on(2)
    [mycursor.execute(f"UPDATE motor SET agitator = {gv.motor[2]} WHERE id = '1'")]
    db.commit()
    time.sleep(172800)
    gv.motor_off(2)
    [mycursor.execute(f"UPDATE motor SET agitator = {gv.motor[2]} WHERE id = '1'")]
    db.commit()


# not sure process line 117-131
def pump_to_tube():
    for round in range(2):
        for pos in range(1,13): #round 1 pos = 1-2 wait for placing
            if pos > 6 or round == 1 : #1-6 and round 0
                [mycursor.execute(f"UPDATE 6_axis_command SET Func_2 = '1' WHERE id = '1'")] #DI2
                db.commit()
                time.sleep(place&pick_tube) 
                while (True): # pick from cen + place on rotator 
                    time.sleep(10)
                    [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_2 WHERE id = '1'")]
                    six_axis = mycursor.fetchone()
                    if six_axis == '0' : break

            # add bioreactor to tube
            time.sleep(2)
            gv.sendArduino()
            [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor[3]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_add_to_tube)
            gv.motor_off(3)
            time.sleep(2)
            gv.write_read("5")
            [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor[3]} WHERE id = '1'")]
            db.commit()

            # rotate tube_rotator1 
            gv.motor_on(4)
            [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor[4]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_move_tube_rotator)
            gv.motor_off(4)
            [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor[4]} WHERE id = '1'")]
            db.commit()

            # (6-axis) move tube to centrifuge process @take_tube position from tube_rotator1 #DI1
            [mycursor.execute(f"UPDATE 6_axis_command SET Func_1 = 1 WHERE id = '1'")] #DI1
            time.sleep(pick_tube)  # time delay ตอนรอ 6-axis ขยับ
            [mycursor.execute(f"SELECT 6_axis FROM motor WHERE id = '1'")]****************
            myresult = mycursor.fetchone()

            while (True): # pick from cen + place on rotator
                time.sleep(10)
                [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_1 WHERE id = '1'")]
                six_axis = mycursor.fetchone()
                if six_axis == '0' : break

            # rotate centrifuge for 1 position....
            gv.motor_on(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_rotate_centrifuge)
            gv.motor_off(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()

            if pos %6 == 0 :  # centrifuge process for 5 mins or else? /not sure the time yet
                # centrifuge roundx.1
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_centrifuge)
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

                if round == 1:
                    for r2 in range(6):
                        [mycursor.execute(f"UPDATE 6_axis_command SET Func_3 = 1 WHERE id = '1'")] #DI3
                        time.sleep(place_tube)  # time delay ตอนรอ 6-axis ขยับ
                        while (True): # pick from cen + place on rotator2 #DI3
                            time.sleep(10)
                            [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_3 WHERE id = '1'")]
                            six_axis = mycursor.fetchone()
                            if six_axis == '0' : break
                        # rotate tube_rotator2
                        gv.motor_on(6)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_move_tube_rotator)
                        gv.motor_off(6)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                        db.commit()

                        # add NaClO into tube
                        gv.motor_on(7)
                        time.sleep(2)
                        gv.sendArduino()
                        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor_on[7]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_add_to_tube)
                        gv.motor_off(7)
                        time.sleep(2)
                        gv.write_read("6")
                        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor_off[7]} WHERE id = '1'")]
                        db.commit()


        if round == 0:
            for pos in range(13,17): #ขาดฟังชั่น centrifuge>>rotator1
                [mycursor.execute(f"UPDATE 6_axis_command SET Func_2 = 1 WHERE id = '1'")] #DI2
                time.sleep(place&pick_tube) 
                while (True): # pick from cen + place on rotator 
                    time.sleep(10)
                    [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_2 WHERE id = '1'")]
                    six_axis = mycursor.fetchone()
                    if six_axis == '0' : break
                
                gv.motor_on(4)
                [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor[4]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_move_tube_rotator)
                gv.motor_off(4)
                [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor[4]} WHERE id = '1'")]
                db.commit()

                # rotate centrifuge for 1 position....
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_rotate_centrifuge)
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()



def NaClO_add():
    # ทิ้ง tube ไว้ 1 hrs b4 centrifuge
    time.sleep(3600)

    for round2 in range(2):
        for pos_cen in range(1,13):
            # rotate tube_rotator2
            gv.motor_on(6)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_move_tube_rotator)
            gv.motor_off(6)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
            db.commit()
            
            # (6-axis) move tube from tube_rotator2 @take_tube position to centrifuge
            [mycursor.execute(f"UPDATE 6_axis_command SET Func_4 = 1 WHERE id = '1'")] #DI4
            time.sleep(place&pick_tube) 
            while (True): # pick from cen + place on rotator 
                time.sleep(10)
                [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_4 WHERE id = '1'")]
                six_axis = mycursor.fetchone()
                if six_axis == '0' : break

            gv.motor_on(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_rotate_centrifuge)
            gv.motor_off(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
#ใช้ฟังชั่นสองตัวแบบนี้ไม่ได้เนื่องจากเวลาในการไปแต่ละตำแหน่งแรคไม่เท่ากัน ต้องแยกกรณี 12 หลุมเลออออ
            if pos_cen == 6: #pos12==func6
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_centrifuge)
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

                for cen_rotate in range(6):
                    [mycursor.execute(f"UPDATE 6_axis_command SET Func_5 = 1 WHERE id = '1'")] #DI5
                    time.sleep(place_to_rack1) 
                    while (True): # pick from cen + place on rotator 
                        time.sleep(10)
                        [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_5 WHERE id = '1'")]
                        six_axis = mycursor.fetchone()
                        if six_axis == '0' : break

                    gv.motor_on(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                    db.commit()
                    time.sleep(t_rotate_centrifuge)
                    gv.motor_off(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                    db.commit()

            elif pos_cen == 12: #pos12==func6
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_centrifuge)
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

                for cen_rotate in range(6):
                    [mycursor.execute(f"UPDATE 6_axis_command SET Func_6 = 1 WHERE id = '1'")] #DI5
                    time.sleep(place_to_rack2) 
                    while (True): # pick from cen + place on rotator 
                        time.sleep(10)
                        [mycursor.execute(f"SELECT 6_axis_feedback FROM Func_6 WHERE id = '1'")]
                        six_axis = mycursor.fetchone()
                        if six_axis == '0' : break

                    gv.motor_on(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                    db.commit()
                    time.sleep(t_rotate_centrifuge)
                    gv.motor_off(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                    db.commit()


if __name__ == '__main__':
    while gv.motor[0] == 0:
        ArduinoRead()
        Process()
    time.sleep(5)
    add_media()
    time.sleep(5)
    add_cell()
    time.sleep(5)
    agitator()
    time.sleep(5)
    pump_to_tube()
    time.sleep(5)
    NaClO_add()


# the pump_to_tube() & NaClO_add() process แบบที่เขียน ยังไม่เหมือนแบบที่ต้องทำให้ได้
# เพราะไม่รู้ว่าจะเขียนโค้ดยังไงให้ระหว่างที่ centrifuge process เทน้ำลง tube อื่นๆยังทำงานต่อไปได้
# แบบที่เขียนน่าจะใช้เวลานานขึ้นกว่าเดิมมาก;-;


## เหลือพาร์ท move tube -> centrifuge วน process ยังไง ยันจบ adding NaClO
## (do we have to consider the time of overall process?)


# the pump_to_tube() & NaClO_add() process แบบที่เขียน ยังไม่เหมือนแบบที่ต้องทำให้ได้
# เพราะไม่รู้ว่าจะเขียนโค้ดยังไงให้ระหว่างที่ centrifuge process เทน้ำลง tube อื่นๆยังทำงานต่อไปได้
# แบบที่เขียนน่าจะใช้เวลานานขึ้นกว่าเดิมมาก
## เหลือพาร์ท move tube -> centrifuge วน process ยังไง ยันจบ adding NaClO
## (do we have to consider the time of overall process?)