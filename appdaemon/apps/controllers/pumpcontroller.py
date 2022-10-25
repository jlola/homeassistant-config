import hassapi as hass

#modde
MODE_ON = "On"
MODE_OFF = "Off"
MODE_AUTO = "Auto"
#input
BINSENSOR_ON = "on"
BINSENSOR_OFF = "off"

#floor_pump_controller:
#   pump_mode: input_select.floor_pump_mode
#   pump_switch: switch.floor_pump
#   min_temp_drum: input_number.pump_t_drum_min
#   temp_drum: input_number.temp_boiler
#   min_temp_tank: input_number.temp_tank_top
#   temp_tank: input_number.pump_t_tank_min
#   thermostat: binary_sensor.thermostat



class PumpController(hass.Hass):
    def initialize(self):
        self.__climate = self.args["climate"]
        self.__servovalue = self.args["servo_value"]
        self.__mode = self.args["pump_mode"]
        self.listen_state(self.mode_callback, self.__mode, attribute = "state")
        self.__pump_switch = self.args["pump_switch"]
        self.listen_state(self.pump_switch_callback, self.__pump_switch, attribute = "state")
        self.__min_temp_drum = self.args["min_temp_boiler"]
        self.listen_state(self.min_temp_drum_callback, self.__min_temp_drum, attribute = "state")
        self.__temp_drum = self.args["temp_boiler"]
        self.listen_state(self.temp_drum_callback, self.__temp_drum, attribute = "state")
        self.__min_temp_tank = self.args["min_temp_tank"]
        self.listen_state(self.min_temp_tank_callback, self.__min_temp_tank, attribute = "state")
        self.__temp_tank = self.args["temp_tank"]
        self.listen_state(self.temp_tank_callback, self.__temp_tank, attribute = "state")
        self.__thermostat = self.args["thermostat"]
        self.listen_state(self.thermostat_callback, self.__thermostat, attribute = "state")
        #priznak, ze je nadrz dostatecne natopena
        self.__tank_is_warm = True
        self.CalculateOutput()

    def trun_climate_on(self,on):
        if (on == True):
            self.call_service("climate/turn_on",entity_id=self.__climate)
        else:
            self.call_service("climate/turn_off",entity_id=self.__climate)

    def set_servo_value(self,value):
        self.set_state(self.__servovalue,state=value)

    def get_mode(self):
        return self.get_state(self.__mode, attribute="state")
    def get_pump_switch(self):
        return self.get_state(self.__pump_switch, attribute="state")
    def get_min_temp_drum(self):
        min_temp_drum = float(self.get_state(self.__min_temp_drum, attribute="state"))
        #self.log(f"min_temp_drum: {min_temp_drum}")
        return min_temp_drum
    def get_temp_drum(self):
        temp_drum = float(self.get_state(self.__temp_drum, attribute="state"))
        return temp_drum
    def get_min_temp_tank(self):
        min_temp_tank = float(self.get_state(self.__min_temp_tank, attribute="state"))
        #self.log(f"min_temp_tank: {min_temp_tank}")
        return min_temp_tank
    def get_temp_tank(self):
        temp_tank_tmp = self.get_state(self.__temp_tank, attribute="state")
        #self.log(f"temp_tank_tmp: {temp_tank_tmp}")
        temp_tank = float(temp_tank_tmp)
        return temp_tank
    def get_thermostat(self):
        thermostatval = self.get_state(self.__thermostat, attribute="state")
        #self.log(f"thermostat: {thermostatval}")
        if (thermostatval==BINSENSOR_ON):
            return True
        else:
            return False


    def thermostat_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()
    def mode_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()
    def pump_switch_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()
    def min_temp_drum_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()
    def temp_drum_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()
    def min_temp_tank_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()
    def temp_tank_callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()

    def CalculateOutput(self):
        self.log(f"CalculateOutput: {self.get_mode()}")
        if (self.get_mode()==MODE_ON):
            self.__turn_pump_on()
        elif (self.get_mode()==MODE_OFF):
            self.__turn_pump_off()
        elif (self.get_mode()==MODE_AUTO):
            self.__auto_output()

    def __auto_output(self):
        self.log(f"auto_output")
        #priznak nahodim jakmile je natopeny kotel
        #shodim ho jakmile klesne teplota nadrze pod limit
        self.log(f"get_temp_drum: {self.get_temp_drum()}, get_min_temp_drum: {self.get_min_temp_drum()}")
        if (self.get_temp_drum() >= self.get_min_temp_drum()):
                self.__tank_is_warm = True
        self.log(f"get_temp_tank: {self.get_temp_tank()}, get_min_temp_tank: {self.get_min_temp_tank()}")
        if (self.get_temp_tank() < self.get_min_temp_tank()):
                self.__tank_is_warm = False
        self.log(f"__tank_is_warm: {self.__tank_is_warm}, thermostat: {self.get_thermostat()}")
        if (self.get_thermostat()==True and (self.get_temp_drum()>=self.get_min_temp_drum() or self.__tank_is_warm)):
            self.__turn_pump_on()
        else: 
            if (self.get_thermostat()==False or (self.get_temp_drum()<self.get_min_temp_drum()-3 and not self.__tank_is_warm)):
                self.__turn_pump_off()

    def __turn_pump_on(self):
        self.log("trun pump on")
        self.__set_pump(True)
        self.trun_climate_on(True)

    def __turn_pump_off(self):
        self.log("trun pump off")
        self.__set_pump(False)
        self.trun_climate_on(False)
        self.set_servo_value(0)

    def __set_pump(self,run):
        #self.log(f"run:{run}")
        if (run==True):
            self.turn_on(self.__pump_switch)
        else:
            self.turn_off(self.__pump_switch)
