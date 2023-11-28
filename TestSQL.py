import mysql.connector

import time
from TestVar import Gaia


# Initialize a variable

# connect to database maybe have to connect with the created database in mySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="delta_gaia",
    database="gaia_properties"
)
mycursor = db.cursor(buffered = True)
gv = Gaia()

mycursor.execute("CREATE DATABASE IF NOT EXISTS gaia_properties")
mycursor.execute("USE gaia_properties")

# Create sensor table //sensor1 = pH, sensor2 = tempt
mycursor.execute("CREATE TABLE IF NOT EXISTS sensor_list (id int PRIMARY KEY AUTO_INCREMENT, pH_sensor FLOAT NOT NULL, tempt_sensor FLOAT NOT NULL)")
mycursor.execute("DESCRIBE sensor_list")

# Create valve table
# valve1 = base buffer, valve2 = acid buffer, valve3 = NaClO
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS valve (id int PRIMARY KEY AUTO_INCREMENT, base_buffer BOOLEAN NOT NULL, acid_buffer BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE valve")

# Create motor table
# motor1 = media, motor2 = cell, motor3= agitator, motor4 = bioreactor, motor5 = tube_rotator1, motor6 = centrifuge, motor7 = tube_rotator_2
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS motor (id int PRIMARY KEY AUTO_INCREMENT, media BOOLEAN NOT NULL, cell BOOLEAN NOT NULL, agitator BOOLEAN NOT NULL, bioreactor BOOLEAN NOT NULL, "
    "tube_rotator1 BOOLEAN NOT NULL, centrifuge BOOLEAN NOT NULL, tube_rotator2 BOOLEAN NOT NULL, NaClO BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE motor")

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

pH = 7
temp = 30
gv.sensor_list[0] = pH
gv.sensor_list[1] = temp

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

Process()
add_media()
add_cell()