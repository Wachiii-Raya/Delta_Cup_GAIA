import serial
import struct
import mysql.connector
import VariableMT as gv
import time
import multiprocessing # ยังไม่ได้ใส่คำสั่งนี้

# Initialize a variable
port = 'COM3', baudrate = 9600 
gp = gaia_platform()

#connect to database maybe have to connect with the created database in mySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="delta_gaia",
    database="Gaia_properties"
)
mycursor = db.cursor()

# Input from serial.read
ser = serial.Serial(port=port, baudrate=baudrate)

# Create Database for mysql server named as Bioreactor //if needed
mycursor.execute("CREATE DATABASE IF NOT EXISTS Gaia_properties")

# Create sensor table //sensor1 = pH, sensor2 = tempt
mycursor.execute("CREATE TABLE IF NOT EXISTS sensor_list (pH_sensor FLOAT NOT NULL, tempt_sensor FLOAT NOT NULL)")
mycursor.execute("DESCRIBE sensor_list")

# Create valve table
    # valve1 = base buffer, valve2 = acid buffer, valve3 = NaCO
mycursor.execute("CREATE TABLE IF NOT EXISTS valve (base_buffer BOOLEAN NOT NULL, acid_buffer BOOLEAN NOT NULL, NaClO BOOLEAN NOT NULL)")
mycursor.execute("DESCRIBE buffer_status")

# Create motor table 
    # motor1 = media, motor2 = cell, motor3= agitator, motor4 = bioreactor, motor5 = tube_rotator1, motor6 = centrifuge, motor7 = tube_rotator_2
mycursor.execute("CREATE TABLE IF NOT EXISTS motor (media BOOLEAN NOT NULL, cell BOOLEAN NOT NULL, agitator BOOLEAN NOT NULL, bioreactor BOOLEAN NOT NULL, tube_rotator1 BOOLEAN NOT NULL, centrifuge BOOLEAN NOT NULL, tube_rotator2 BOOLEAN NOT NULL, id int PRIMARY KEY AUTO_INCREMENT)") 
mycursor.execute("DESCRIBE motor_status")

db.commit()

# do 2 functions at the same time
def MultiProcessing():
    #how to;-;
    print('read dis one: https://linuxhint.com/python-multiprocessing-example/')


def ArduinoRead():
    # Read data from arduino UNO 
    # not sure chfff smth
    # **python arduino struct read: https://stackoverflow.com/questions/60306952/how-to-read-a-data-struct-sent-serially-from-an-arduino
    while True:
        cc = bytearray(ser.readline())
        if len(cc) == 10:  # package variable ที่จะส่งมาจาก arduino # not sure number of the board
            sensor_list = list(struct.unpack('ffh', cc))[:] #returned as elements of tuple
            [mycursor.execute(f"UPDATE sensor_list SET pH_sensor = {val}, val in enumerate(sensor_list))"]
   [mycursor.execute(f"UPDATE sensor_list SET temp_sensor = {val}, val in enumerate(sensor_list)"]
            db.commit()
            features_list = gv.create_features_list(sensors_list)

def Process():
    while gv.motor[0] == 0:
        gv.pHChecker()       
        [mycursor.execute(f"UPDATE valve SET base_buffer = %d", ['valve'][f'valve[0]'])] 
        [mycursor.execute(f"UPDATE valve SET acid_buffer = %d", ['valve'][f'valve[1]'])]
        db.commit()
        time.sleep(5)
        [mycursor.execute(f"UPDATE valve SET base_buffer = 0")] 
        [mycursor.execute(f"UPDATE valve SET acid_buffer = 0")]
        db.commit()
        time.sleep(60) # รอให้ buffer mix with media แล้วค่อย recheck not sure

    def add_media(): # add 80% of 5 L = 4 L
        [mycursor.execute(f"UPDATE motor SET media = %d", gv.motor_on(0))]
        db.commit()
        time.sleep(t_add_media)
        [mycursor.execute(f"UPDATE motor SET meida = %d", gv.motor_off(0))]
        db.commit()

    def add_cell(): # add 20% of 5 L = 1 L
        [mycursor.execute(f"UPDATE motor SET cell = %d", gv.motor_on(1))]
        db.commit()
        time.sleep(t_add_cell) 
        [mycursor.execute(f"UPDATE motor SET cell = %d", gv.motor_off(1))]
        db.commit()

    def agitator():
        [mycursor.execute(f"UPDATE motor SET agitator = %d", gv.motor_on(2))]
        db.commit()
        time.sleep(172800)
        [mycursor.execute(f"UPDATE motor SET agitator = %d", gv.motor_off(2))]
        db.commit()

   

    # not sure process line 117-131
    def pump_to_tube():
        for round in range(2):
            pos = 0
            i=1
            for i in range(17):
                if i <= 12: #หลอด1-12
                  # add bioreactor to tube
                    mycursor.execute(f"UPDATE motor SET bioreactor = %d", gv.motor_on(3))
                    db.commit()
                    time.sleep(t_add_to_tube)
                    [mycursor.execute(f"UPDATE motor SET bioreactor = %d", gv.motor_off(3))]
                    db.commit()

                    [mycursor.execute(f"UPDATE motor SET tube_rotator1 = %d", gv.motor_on(4))]
                    db.commit()
                    time.sleep(t_move_tube_rotator)
                    [mycursor.execute(f"UPDATE motor SET tube_rotator1 = %d", gv.motor_off(4))]
                    pos += 1
                    time.sleep(t_gotocentrifuge_delay) 
                    # (6-axis) move tube to centrrotator1
    #centrifuge ทำยังไงให้รัน while นี้ไปด้วยพร้อมกับขยับค่า i จนครบ 16 tube? multiprocessing?
                    if pos % 6 == 0:      # centrifuge process for 5 mins or else? หลุม 16
       # (6-axis) move tube to centrifuge process
                        [mycursor.execute(f"UPDATE motor SET centrifuge = %d", gv.motor_on(5))]
                        db.commit()
                        time.sleep(300) 
                        [mycursor.execute(f"UPDATE motor SET centrifuge = %d", gv.motor_off(5))]

                        if round == 0:
                            # (6-axis) pouring waste process + move to tube rotator1
                            for s_0 o=in range(6):
                                time.sleep(t_rotator1_delay) 
                                [mycursor.execute(f"UPDATE motor SET tube_rotator1 = %d", gv.motor_on(4))]
                                db.commit()
                                time.sleep(t_move_tube_rotator)
                                [mycursor.execute(f"UPDATE motor SET tube_rotator1 = %d", gv.motor_off(4))]
                        else: # round == 1
                            # (6-axis) pouring waste process + move to tube rotator2
                            for s_1 in range(6):
                                time.sleep(t_rotator2_delay) 
                                [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_on(6))]
                                db.commit()
                                time.sleep(t_move_tube_rotator)
                                [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_off(6))]
                                db.commit()
                    else: pass
                else: #ปล่อยฟรีหบุม13-16 
    # (6-axis) move tube rotator1
                    [mycursor.execute(f"UPDATE motor SET tube_rotator1 = %d", gv.motor_on(4))]
                    db.commit()
                    time.sleep(t_move_tube_rotator)
                    [mycursor.execute(f"UPDATE motor SET tube_rotator1 = %d", gv.motor_off(4))]
    
    def NaClO_add():
        for s_1 in range (): #หมนฟรี 4 รอบ tube rotator2 
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_on(6))]
            db.commit()
            time.sleep(t_move_tube_rotator)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_off(6))]
            db.commit()

        for i in range(12):
            #add NaClO into tube
            [mycursor.execute(f"UPDATE valve SET NaClO = 1")]
            db.commit()
            time.sleep(t_add_to_tube)
            [mycursor.execute(f"UPDATE valve SET NaClO = 0")]
            db.commit()

            # rotate tube_rotator2
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_on(6))]
            db.commit()
            time.sleep(t_move_tube_rotator)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_off(6))]
            db.commit()

        # ทิ้ง tube ไว้ 1 hrs b4 centrifuge
        time.sleep(3600)
 
        pos_2=1
        for pos_2 in range(13):
  # move tube into centrifuge
  # rotate tube_rotator2
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_on(6))]
            db.commit()
            time.sleep(t_move_tube_rotator)
            [mycursor.execute(f"UPDATE motor SET tube_rotator2 = %d", gv.motor_off(6))]
            db.commit()
            if pos_2 % 6 == 0:
   # centrifuge for 15 mins
                [mycursor.execute(f"UPDATE motor SET centrifuge = %d", gv.motor_on(5))]
                db.commit()
                time.sleep(900) 
                [mycursor.execute(f"UPDATE motor SET centrifuge = %d", gv.motor_off(5))]

                    # (6-axis) pouring waste process + move to the prepared rack
            else: pass
            
            

# the pump_to_tube() & NaClO_add() process แบบที่เขียน ยังไม่เหมือนแบบที่ต้องทำให้ได้ 
# เพราะไม่รู้ว่าจะเขียนโค้ดยังไงให้ระหว่างที่ centrifuge process เทน้ำลง tube อื่นๆยังทำงานต่อไปได้
# แบบที่เขียนน่าจะใช้เวลานานขึ้นกว่าเดิมมาก;-;


            


                
                
## เหลือพาร์ท move tube -> centrifuge วน process ยังไง ยันจบ adding NaClO
## (do we have to consider the time of overall process?)


# the pump_to_tube() & NaClO_add() process แบบที่เขียน ยังไม่เหมือนแบบที่ต้องทำให้ได้ 
# เพราะไม่รู้ว่าจะเขียนโค้ดยังไงให้ระหว่างที่ centrifuge process เทน้ำลง tube อื่นๆยังทำงานต่อไปได้
# แบบที่เขียนน่าจะใช้เวลานานขึ้นกว่าเดิมมาก;-;


            


                
                
## เหลือพาร์ท move tube -> centrifuge วน process ยังไง ยันจบ adding NaClO
## (do we have to consider the time of overall process?)