import hassapi as hass

MODE_ELECTRIC = "Electric"
MODE_BOILER = "Boiler"
MODE_AUTO = "Auto"

KEY_ELECTRIC_HEAT_DISCONNECT = "switch_electric_heat_disconnect"
KEY_TEMP_TANK = "temp_tank"
KEY_TEMP_BOILER = "temp_boiler"
KEY_MODE = "water_heater_mode"
KEY_ACTUAL_MODE = "actual_mode_select"
KEY_MIN_TEMP_TANK = "min_temp_tank"
KEY_MIN_TEMP_BOILER = "min_temp_boiler"
KEY_SERVO_WATERHEATER = "servo_water_heater"
KEY_PUMP_WATERHEATER = "pump_water_heater"
KEY_WATER_HEATER_TEMPERATURE = "water_heater_temperature"
KEY_CLIMATE_THERMOSTAT = "climate_thermostat"

#waterheatercontroller:
#   water_heater_mode: input_select.water_heater_mode
#   switch_water_heater_mode: switch.switch_5_14_waterheater_mode
#   temp_tank: sensor.temp_tank_top
#   temp_boiler: sensor.temp_boiler
#   min_temp_tank: input_number.min_temp_tank_water_heater
#   min_temp_boiler: input_number.min_temp_boiler_water_heater
#   servo_water_heater: switch.switch_5_15_servo_waterheater
#   water_heater_temperature: sensor.3_temperature_waterheater
#   climate_thermostat: climate.climate_waterheater
#   pump_water_heater: switch.switch_5_9_pump_waterheater

class WaterHeaterController(hass.Hass):
    def initialize(self):
        self.listen_state(self.callback, self.args[KEY_ELECTRIC_HEAT_DISCONNECT], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_TEMP_TANK], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_TEMP_BOILER], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_MODE], attribute = "state")        
        self.listen_state(self.callback, self.args[KEY_MIN_TEMP_TANK], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_MIN_TEMP_BOILER], attribute = "state")
        self.listen_state(self.OnServoState, self.args[KEY_SERVO_WATERHEATER], attribute = "state")
        self.__climate = self.args[KEY_CLIMATE_THERMOSTAT]

    def OnServoState(self, entity, attribute, old, new, kwargs):
        self.log(f"OnServoState run:{self.IsServoRun()}")
        if (self.IsServoRun()=="on"):
            self.__pump_waterheater_on(True)
        else:
            self.__pump_waterheater_on(False)

    def IsServoRun(self):
        return self.get_state(self.args[KEY_SERVO_WATERHEATER], attribute="state")
    

    def CalculateOutput(self):
        __switch_boiler = self.get_state(self.args[KEY_ELECTRIC_HEAT_DISCONNECT], attribute="state")
        __temp_tank = float(self.get_state(self.args[KEY_TEMP_TANK], attribute="state"))
        __temp_boiler = float(self.get_state(self.args[KEY_TEMP_BOILER], attribute="state"))
        __modeRequest = self.get_state(self.args[KEY_MODE], attribute="state")
        __min_temp_tank = float(self.get_state(self.args[KEY_MIN_TEMP_TANK], attribute="state"))
        __min_temp_boiler = float(self.get_state(self.args[KEY_MIN_TEMP_BOILER], attribute="state"))
        __servo_waterheater = self.get_state(self.args[KEY_SERVO_WATERHEATER], attribute="state")        
        if (__modeRequest == MODE_ELECTRIC):
            self.__electric_heat_disconnect(False)
            self.turn_climate_on(False)
        elif (__modeRequest == MODE_BOILER):
            self.__electric_heat_disconnect(True)
            self.turn_climate_on(True)
        elif (__modeRequest == MODE_AUTO):
            if (__temp_tank > __min_temp_tank or __temp_boiler > __min_temp_boiler):
                self.__electric_heat_disconnect(True)
                self.turn_climate_on(True)
            elif ((__temp_tank < (__min_temp_tank - 5.0)) or (__temp_boiler < (__min_temp_boiler - 5.0))):
                self.__electric_heat_disconnect(False)
                self.turn_climate_on(False)

    def callback(self, entity, attribute, old, new, kwargs):
        self.log(f"callback {entity}")
        self.CalculateOutput()

    def __electric_heat_disconnect(self,boiler):
        #self.log(f"run:{run}")
        if (boiler==True):
            self.turn_on(self.args[KEY_ELECTRIC_HEAT_DISCONNECT])
        else:
            self.turn_off(self.args[KEY_ELECTRIC_HEAT_DISCONNECT])

    def __pump_waterheater_on(self,run):
        self.log(f"__pump_waterheater_on run:{run}")
        if (run==True):
            self.turn_on(self.args[KEY_PUMP_WATERHEATER])
        else:
            self.turn_off(self.args[KEY_PUMP_WATERHEATER])
    
    def turn_climate_on(self,on):
        if (on == True):
            self.call_service("climate/turn_on",entity_id=self.__climate)
        else:
            self.call_service("climate/turn_off",entity_id=self.__climate)
