from math import sqrt

class Gaia :
    def __init__(self):
        self.GaiaProperty_dict = {'sensor': {'sensor1': 0.0, 'sensor2': 0.0},
                                  'valve': {'valve1': 0, 'valve2': 0},
                                  'motor': {'motor1': 0, 'motor2': 0, 'motor3': 0, 'motor4': 0, 'motor5': 0,
                                            'motor6': 0, 'motor7': 0, 'motor8': 0}
                                  }

        self.sensor_list = [0, 0]
        self.valve = [0, 0]
        self.motor = [0, 0, 0, 0, 0, 0, 0, 0]

        self.Min_pHSensor = 6
        self.Max_pHSensor = 8

    def create_sensorFeatures_list(self):
        sensor_list = []
        [sensor_list.append(self.GaiaProperty_dict['sensor'][f'sensor{i + 1}']) for i in
         range(len(self.GaiaProperty_dict['sensor']))]
        self.update_sensorFeatures_dict(sensor_list)
        return sensor_list

    def create_valveFeatures_list(self):
        valve_list = []
        [valve_list.append(self.GaiaProperty_dict['valve'][f'valve{i + 1}']) for i in
         range(len(self.GaiaProperty_dict['valve']))]
        self.update_valveFeatures_dict(valve_list)
        return valve_list

    def create_motorFeatures_list(self):
        motor_list = []
        [motor_list.append(self.GaiaProperty_dict['motor'][f'motor{i + 1}']) for i in
         range(len(self.GaiaProperty_dict['motor']))]
        self.update_motorFeatures_dict(motor_list)
        return motor_list

    def pHacid(self):
        self.valve[0] = 1
        self.valve[1] = 0

    def pHbase(self):
        self.valve[0] = 0
        self.valve[1] = 1

    def pHChecker(self):
        if self.sensor_list[0] < self.Min_pHSensor:
            self.pHacid()
        elif self.sensor_list[0] > self.Max_pHSensor:
            self.pHbase()
        else:  # pH in range
            self.motor[0] = 1

    def motor_on(self, i):
        self.motor[i] = 1

    def motor_off(self, i):
        self.motor[i] = 0

    def update_sensorFeatures_dict(self, sensor_list):
        [self.GaiaProperty_dict['sensor'].update(
            {f'sensor{i + 1}': (self.GaiaProperty_dict['sensor_init'][f'sensor{i + 1}'] - sensor_list[i])}) for i in
         range(len(self.GaiaProperty_dict['sensor']))]

    def update_valveFeatures_dict(self, valve_list):
        [self.GaiaProperty_dict['valve'].update(
            {f'valve{i + 1}': (self.GaiaProperty_dict['valve_init'][f'valve{i + 1}'] - valve_list[i])}) for i in
         range(len(self.GaiaProperty_dict['valve']))]

    def update_motorFeatures_dict(self, motor_list):
        [self.GaiaProperty_dict['motor'].update(
            {f'motor{i + 1}': (self.GaiaProperty_dict['motor_init'][f'motor{i + 1}'] - motor_list[i])}) for i in
         range(len(self.GaiaProperty_dict['motor']))]
    # self เขียนไง
    # ต้อง update mai


if __name__ == "__main__":  # which information do we have to display in this project?
    gv = Gaia()
    print(Gaia.GaiaProperty_dict)
    plist = [50, 50]  # อันนี้เอาไว้ทำอะไร
    features_list = gv.create_sensorFeatures_list(plist)
    print(f"features_list: {features_list}")
    print(f"length of features_list: {len(features_list)}")