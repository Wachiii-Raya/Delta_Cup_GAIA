import serial
import struct
import mysql.connector
import Gaia_variable 
import time
import multiprocessing  # ยังไม่ได้ใส่คำสั่งนี้

# Initialize a variable
port = 'COM3', baudrate = 9600
gv = Gaia_variable()

# connect to database maybe have to connect with the created database in mySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="delta_gaia",
    database="Gaia_properties"
)
mycursor = db.cursor(buffered = True)

# Input from serial.read
ser = serial.Serial(port=port, baudrate=baudrate)

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
mycursor.execute("DESCRIBE buffer_status")

# Create motor table
# motor1 = media, motor2 = cell, motor3= agitator, motor4 = bioreactor, motor5 = tube_rotator1, motor6 = centrifuge, motor7 = tube_rotator_2, motor8 = NaClO
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS motor (id int PRIMARY KEY AUTO_INCREMENT, media BOOLEAN NOT NULL, cell BOOLEAN NOT NULL, agitator BOOLEAN NOT NULL, bioreactor BOOLEAN NOT NULL, "
    "tube_rotator1 BOOLEAN NOT NULL, centrifuge BOOLEAN NOT NULL, tube_rotator2 BOOLEAN NOT NULL, NaClO BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE motor_status")

db.commit()

[mycursor.execute(f"SELECT * FROM sensor_list")]
[mycursor.execute(f"SELECT * FROM valve")]
[mycursor.execute(f"SELECT * FROM motor")]
[mycursor.execute(f"INSERT INTO sensor_list(pH_sensor,tempt_sensor) VALUES (0,0)")]
[mycursor.execute(f"INSERT INTO valve(base_buffer, acid_buffer) VALUES (0,0)")]
[mycursor.execute(f"INSERT INTO motor(media, cell, agitator, bioreactor, tube_rotator1, centrifuge, tube_rotator2, NaClO) VALUES (0,0,0,0,0,0,0,0)")]
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
            pH = round(sensor_list[0], 5)
            temp = round(sensor_list[1], 3)
            [mycursor.execute(f"UPDATE sensor_list SET pH_sensor = '{pH}' WHERE id = '1'")]
            [mycursor.execute(f"UPDATE sensor_list SET temp_sensor = '{temp}' WHERE id = '1'")]
            db.commit()
            features_list = gv.create_features_list(sensor_list)

def Process():
    while gv.motor[0] == 0:
        gv.pHChecker()
        [mycursor.execute(f"UPDATE valve SET base_buffer = {gv.GaiaProperty_dict['valve'][f'valve{1}']} WHERE id = '1'", )]
        [mycursor.execute(f"UPDATE valve SET acid_buffer = {gv.GaiaProperty_dict['valve'][f'valve{2}']} WHERE id = '1'", )]
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
    time.sleep(10)
    gv.motor_off(0)
    [mycursor.execute(f"UPDATE motor SET media = {gv.motor[0]} WHERE id = '1'")]
    db.commit()


def add_cell():  # add 20% of 5 L = 1 L
    gv.motor_on(1)
    [mycursor.execute(f"UPDATE motor SET cell = {gv.motor[1]} WHERE id = '1'")]
    db.commit()
    time.sleep(10)
    gv.motor_off(1)
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

# not sure process
def pump_to_tube():
    for round in range(2):
        pos = 0
        while pos <= 6:
            # add bioreactor to tube
            gv.motor_on(3)
            [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor[3]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_add_to_tube)
            gv.motor_off(3)
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

            # (6-axis) move tube to centrifuge process @take_tube position from tube_rotator1
            time.sleep(t_for_6axis) # time delay ตอนรอ 6-axis ขยับ

            # rotate centrifuge for 1 position....
            gv.motor_on(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_rotate_centrifuge)
            gv.motor_off(5)
            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
            db.commit()

            pos += 1
            
            if pos == 6:      # centrifuge process for 5 mins or else? /not sure the time yet
                # centrifuge roundx.1
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_centrifuge) 
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

                if round == 0:
                    for pos_centri1 in range(6):
                        # (6-axis) taking tube from centrifuge & pouring waste 
                        # (6-axis) & taking back the tube to tube_rotator1 @return_tube position
                        time.sleep(t_delay_for_6axis)

                        # add bioreactor to tube
                        gv.motor_on(3)
                        [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor_on[3]} WHERE id = '1'")]
                        time.sleep(t_add_to_tube)
                        gv.motor_off(3)
                        [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor_off[3]} WHERE id = '1'")]
                        db.commit()

                        # rotate tube_rotator1
                        gv.motor_on(4)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor_on[4]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_move_tube_rotator)
                        gv.motor_off(4)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor_off[4]} WHERE id = '1'")]
                        db.commit()

                        # (6-axis) move tube to centrifuge process @take_tube position from tube_rotator1
                        time.sleep(t_delay_for_6axis)

                        if pos_centri1 <= 5:
                            # (6-axis) rotate centrifuge for 1 position
                            gv.motor_on(5)
                            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor_on[5]} WHERE id = '1'")]
                            db.commit()
                            time.sleep(t_rotate_centrifuge)
                            gv.motor_off(5)
                            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor_off[5]} WHERE id = '1'")]
                            db.commit()
                        
                        else: pass
                    
                    # centrifuge roundx.2
                    gv.motor_on(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor_on[5]} WHERE id = '1'")]
                    db.commit()
                    time.sleep(t_centrifuge) 
                    gv.motor_off(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor_off[5]} WHERE id = '1'")]
                    db.commit()

                    for pos_centri2 in range(6):
                        # (6-axis) move tube to centrifuge process @take_tube position from tube_rotator1
                        time.sleep(t_delay_for_6axis)

                        # (6-axis) rotate centrifuge for 1 position
                        gv.motor_on(5)
                        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor_on[5]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_rotate_centrifuge)
                        gv.motor_off(5)
                        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor_off[5]} WHERE id = '1'")]
                        db.commit()

                        # rotate tube_rotator1
                        gv.motor_on(4)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor_on[4]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_move_tube_rotator)
                        gv.motor_off(4)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor_off[4]} WHERE id = '1'")]
                        db.commit()

                    # reset location of tube_rotator1 to be @ origin
                    gv.motor_on(4)
                    [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor_on[4]} WHERE id = '1'")]
                    db.commit()
                    time.sleep(t_move_tube_rotator_to_origin)
                    gv.motor_off(4)
                    [mycursor.execute(f"UPDATE motor SET tube_rotator1 = {gv.motor_off[4]} WHERE id = '1'")]
                    db.commit()

                    pos += 1
                
                else: # round == 1
                    for pos_centri3 in range(6):
                        # (6-axis) pouring waste process + move to tube rotator2 @return_tube position
                        time.sleep(t_delay_for_6axis)

                        # rotate tube_rotator2
                        gv.motor_on(6)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_move_tube_rotator)
                        gv.motor_off(6)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                        db.commit()

                        #add NaClO into tube
                        gv.motor_on(7)
                        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor_on[7]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_add_to_tube)
                        gv.motor_off(7)
                        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor_off[7]} WHERE id = '1'")]
                        db.commit()

                        # add bioreactor to tube
                        gv.motor_on(3)
                        [mycursor.execute(f"UPDATE motor SET bioreactor = {gv.motor[3]} WHERE id = '1'")]
                        time.sleep(t_add_to_tube)
                        gv.motor_off(3)
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

                        # (6-axis) move tube to centrifuge process @take_tube position from tube_rotator1
                        time.sleep(t_delay_for_6axis)

                        if pos_centri3 <= 5:
                            # (6-axis) rotate centrifuge for 1 position
                            gv.motor_on(5)
                            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                            db.commit()
                            time.sleep(t_rotate_centrifuge)
                            gv.motor_off(5)
                            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                            db.commit()

                        else: pass

                    # centrifuge roundx.2
                    gv.motor_on(5)
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                    db.commit()
                    time.sleep(t_centrifuge)
                    gv.motor_off(5) 
                    [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                    db.commit()

                    for pos_centri4 in range(6):
                        # (6-axis) pouring waste process + move to tube rotator2 @return_tube position
                        time.sleep(t_delay_for_6axis)

                        # rotate tube_rotator2
                        gv.motor_on(6)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_move_tube_rotator)
                        gv.motor_off(6)
                        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
                        db.commit()

                        #add NaClO into tube
                        gv.motor_on(7)
                        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor_on[7]} WHERE id = '1'")]
                        db.commit()
                        time.sleep(t_add_to_tube)
                        gv.motor_off(7)
                        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor_off[7]} WHERE id = '1'")]
                        db.commit()

                        if pos_centri4 <= 5:
                            # (6-axis) rotate centrifuge for 1 position
                            gv.motor_on(5)
                            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                            db.commit()
                            time.sleep(t_rotate_centrifuge)
                            gv.motor_off(5)
                            [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                            db.commit()

                        else: pass
                    pos += 1
                
            else: pass

def NaClO_add():
    # reset location of tube_rotator2 to be @ origin
    gv.motor_on(6)
    [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
    db.commit()
    time.sleep(t_move_tube_rotator_to_origin)
    gv.motor_off(6)
    [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
    db.commit()

    for pos_tube in range(12):
        # (6-axis) pouring waste process + move to tube rotator2 @return_tube position
        time.sleep(t_delay_for_6axis)

        # rotate tube_rotator2
        gv.motor_on(6)
        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
        db.commit()
        time.sleep(t_move_tube_rotator)
        gv.motor_off(6)
        [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
        db.commit()

        #add NaClO into tube
        gv.motor_on(7)
        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor[7]} WHERE id = '1'")]
        db.commit()
        time.sleep(t_add_to_tube)
        gv.motor_off(7)
        [mycursor.execute(f"UPDATE motor SET NaClO = {gv.motor[7]} WHERE id = '1'")]
        db.commit()

    # ทิ้ง tube ไว้ 1 hrs b4 centrifuge
    time.sleep(3600)
    
    for round2 in range(2):
        for pos_centri5 in range(6):
            # (6-axis) move tube from tube_rotator2 @take_tube position to centrifuge
            time.sleep(t_delay_for_6axis)

            # rotate tube_rotator2
            gv.motor_on(6)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
            db.commit()
            time.sleep(t_move_tube_rotator)
            gv.motor_off(6)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = {gv.motor[6]} WHERE id = '1'")]
            db.commit()

            if pos_centri5 <= 5:
                # (6-axis) rotate centrifuge for 1 position
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_rotate_centrifuge)
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

            pass
        
        gv.motor_on(5)
        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
        db.commit()
        time.sleep(t_centrifuge) 
        gv.motor_off(5)
        [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]

        for pos_centri6 in range(6):
            # (6-axis) move tube from centrifuge and put to rack
            time.sleep(t_delay_for_6axis)

            if pos_centri6 <= 5:
                # (6-axis) rotate centrifuge for 1 position
                gv.motor_on(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()
                time.sleep(t_rotate_centrifuge)
                gv.motor_off(5)
                [mycursor.execute(f"UPDATE motor SET centrifuge = {gv.motor[5]} WHERE id = '1'")]
                db.commit()

            pass

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