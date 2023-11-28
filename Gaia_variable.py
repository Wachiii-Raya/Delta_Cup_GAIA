from math import sqrt
import time #ยังไม่ได้ลง env

class BioreactorAdjustment:
    def __init__(self):
        self.sensors_list       =   [0.0, 0.0]
        self.motors_list        =   [False, False, False, False, False, False, False]
        self.valves_list        =   [False, False, False]

    def create_sensor_list(self, sensors_list):
        sensors_list = []                               #sensors_list[0] = pH sensor(id = 1),  sensors_list[1] = tempsensor
        sensors_list.append(sensors_list[idx] for idx in enumerate(sensors_list))
        self.update_sensor_list(sensors_list)
        return sensors_list

    def check_pH(self, sensors_list):
     	''' sensors_list[0] = pH sensor(id = 1), valves_list[0] = acid buffer(id = 1), valves_list[1] = base buffer(id = 2)'''
        while sensors_list[0] not in range(6.0,8.0):
            if sensors_list[0] > 8.0 :
                self.valves_list[0], self.valves_list[1] = True, False      #turn on valve1, turn off valve2
                time.sleep(1000)                                            #เปิดกี่นาที?
                self.valves_list[0], self.valves_list[1] = False, False     #turn off both
            else:
                self.valves_list[0], self.valves_list[1] = False, True      #turn on valve 2, turn off valve 1
                time.sleep(1000)                                            #เปิดกี่นาที?
                self.valves_list[0], self.valves_list[1] = False, False     #turn off both
        return self.valves_list[0], self.valves_list[1]
        
    def bioreactor(self):
        ''' motors_list[0] = media tank(id = 1), motors_list[1] = cell tank(id = 2), motors_list[2] = agitator(id = 3),  sensors_list[1] = temp sensor(id = 2)'''
        self.motors_list[0] = True      #turn on pump at media tank
        self.motors_list[1] = True      #turn on pump at cell tank
        time.sleep(1000)                #time?
        self.motors_list[0] = False     #turn off pump at media tank 
        self.motors_list[1] = False     #turn off pump at cell tank
        self.motors_list[2] = True      #turn on agitator
        time.sleep(172800)              # 48 hrs
        self.motors_list[2] = False     #turn off agitator
        time.sleep(100)                 # แบบให้ชัวร์ว่า agitator หยุดหมุนก่อนละเปิดปั๊ม

    def tube_rotator1(self):
        '''motors_list[3] = pump biomass out(id = 4), motors_list[4] = tube rotator(id = 5), mortors_list[5] = centrifuge(id = 6)'''
        for round in round(4):                  #เติม Biomass 4 ครั้ง
            for position in position(6):        #อาจจะลดเหลือ 6 หลุม
                self.motors_list[3] = True      #turn on pump at bioreactor
                time.sleep(1000)                #time: pumping biomass out? 25 ml
                self.motors_list[3] = False     #turn off pump at bioreactor
                self.motors_list[4] = True      #turn on tube rotator1
                time.sleep(1000)                #time? for 1 position
                self.motors_list[4] = False     #turn off tube rotator1
                time.sleep(2000)                #time: moving tube to centrifuge by 6-axis
            self.motors_list[5] = True          #turn on centrifuge
            time.sleep(2500)                    #centrifuge duration? 5 minutes + trash + move tubes back     
            self.motors_list[5] = False         #turn off centrifuge
        time.sleep(10000)                       #time for moving 16 tubes to tube rotator2 by 6-axis

    def tube_rotator2(self):
        '''mortors_list[5] = centrifuge(id = 6), mortors_list[6] = tube_rotator2(id = 7), valves_list[2] = NaCl(id = 3)'''
        for round in round(2):                  #เติม NaCl 2 ครั้ง
            for position in position(6):
                self.valves_list[2] = True      #turn on valve at NaCl tank
                time.sleep(1000)                #เติมสารกี่วิ ซุยเลย ไม่ต้องละเอียดมาก
                self.valves_list[2] = False     #turn off valve at NaCl tank
                self.motors_list[6] = True      #turn on tube rotator2
                time.sleep(1000)                #time? for 1 position
                self.motors_list[6] = False     #turn off tube rotator2
                time.sleep(2000)                #time: moving tube to centrifuge by 6-axis 
            self.motors_list[5] = True          #turn on centrifuge
            time.sleep(2500)                    #centrifuge duration? 5 minutes + trash + move tubes back
            self.motors_list[5] = False         #turn off centrifuge
        