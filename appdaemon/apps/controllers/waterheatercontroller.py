import hassapi as hass

MODE_ELECTRIC = "Electric"
MODE_BOILER = "Boiler"
MODE_AUTO = "Auto"

KEY_SWITCH_BOILER = "switch_water_heater_mode"
KEY_TEMP_TANK = "temp_tank"
KEY_TEMP_BOILER = "temp_boiler"
KEY_MODE = "water_heater_mode"
KEY_WATERHEATER_THEROMOSTAT = "water_heater_thermostat"
KEY_MIN_TEMP_TANK = "min_temp_tank"
KEY_MIN_TEMP_BOILER = "min_temp_boiler"
KEY_SERVO_WATERHEATER = "servo_water_heater"

#waterheatercontroller:
#   water_heater_mode: input_select.water_heater_mode
#   switch_water_heater_mode: switch.switch_5_14_waterheater_mode
#   temp_tank: sensor.temp_tank_top
#   temp_boiler: sensor.temp_boiler
#   water_heater_thermostat: binary_sensor_5_2_waterheater_thermostat
#   min_temp_tank: input_number.min_temp_tank_water_heater
#   min_temp_boiler: input_number.min_temp_boiler_water_heater
#   servo_water_heater: switch.switch_5_15_servo_waterheater

class WaterHeaterController(hass.Hass):
    def initialize(self):
        #self.listen_state(self.callback, self.args[KEY_SWITCH_BOILER], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_TEMP_TANK], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_TEMP_BOILER], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_MODE], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_WATERHEATER_THEROMOSTAT], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_MIN_TEMP_TANK], attribute = "state")
        self.listen_state(self.callback, self.args[KEY_MIN_TEMP_BOILER], attribute = "state")
        #self.listen_state(self.callback, self.args[KEY_SERVO_WATERHEATER], attribute = "state")

    def CalculateOutput(self):
        __switch_boiler = self.get_state(self.args[KEY_SWITCH_BOILER], attribute="state")
        __temp_tank = self.get_state(self.args[KEY_TEMP_TANK], attribute="state")
        __temp_boiler = self.get_state(self.args[KEY_TEMP_BOILER], attribute="state")
        __mode = self.get_state(self.args[KEY_MODE], attribute="state")
        __waterheater_thermostat = self.get_state(self.args[KEY_WATERHEATER_THEROMOSTAT], attribute="state")
        __min_temp_tank = self.get_state(self.args[KEY_MIN_TEMP_TANK], attribute="state")
        __min_temp_boiler = self.get_state(self.args[KEY_MIN_TEMP_BOILER], attribute="state")
        __servo_waterheater = self.get_state(self.args[KEY_SERVO_WATERHEATER], attribute="state")
        if (__mode == MODE_ELECTRIC):
            self.__set_heat_by_boiler(False)
        elif (__mode == MODE_BOILER):
            self.__set_heat_by_boiler(True)
        elif (__mode == MODE_AUTO):
            if ((__temp_tank > __min_temp_tank or __temp_boiler > __min_temp_boiler) and __waterheater_thermostat=="Heat" ):
                self.__set_heat_by_boiler(True)
            else:
                self.__set_heat_by_boiler(False)

    def callback(self, entity, attribute, old, new, kwargs):
        self.CalculateOutput()

    def __set_heat_by_boiler(self,boiler):
        #self.log(f"run:{run}")
        if (boiler==True):
            self.turn_on(self.args[KEY_SWITCH_BOILER])
        else:
            self.turn_off(self.args[KEY_SWITCH_BOILER])
