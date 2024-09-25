import hassapi as hass

KEY_PUMP_SWITCH = "pool_pump_switch"
KEY_POOL_PUMP_BUTTON = "pool_pump_button"
KEY_POOL_PUMP_MODE = "poolpump_mode"
KEY_TEMP_SOLAR_PANEL = "temperature_solar_panel"
KEY_POOL_PUMPE_TEMP_TURNON_LIMIT = "pool_pumpe_temperature_turnon_limit"
KEY_POOL_PUMPE_TEMP_TURNOFF_LIMIT = "pool_pumpe_temperature_turnoff_limit"

#pool_pump_controller:
#  module: PoolPumpController
#  pool_pump_switch: switch.switch_7_7_pool_pump
#  pool_pump_button: binary_input.binary_sensor_7_1_pool_pump_button
#  set_temperature_pump_turn_on:
#  set_temperature_pump_turn_off:
#  temperature_solar_panel: sensor.temp_solar_heater
#  poolpump_mode: input_select.solar_pump_mode
#  set_automatic:
#  set_manual: 

SOLARPUMP_MODE_ON = "On"
SOLARPUMP_MODE_OFF = "Off"
SOLARPUMP_MODE_AUTO = "Auto"
SOLARPUMP_MODE_SWIMMING = "Swimming"

# Declare Class
class PoolPumpController(hass.Hass):
    def initialize(self):
        self.listen_state(self.button_callback, self.args[KEY_POOL_PUMP_BUTTON], attribute = "state")
        self.listen_state(self.pool_pump_mode_callback, self.args[KEY_POOL_PUMP_MODE], attribute = "state")
        self.listen_state(self.temperature_solar_panel_callback, self.args[KEY_TEMP_SOLAR_PANEL], attribute = "state")
        self._firstRun = True
        self._mode = self.args[KEY_POOL_PUMP_MODE]

    def __pump_pool_on(self,run):
        self.log(f"__pump_pool_on run:{run}") 
        if (run==True):
            self.turn_on(self.args[KEY_PUMP_SWITCdefH])
        else:
            self.turn_off(self.args[KEY_PUMP_SWITCH])

    def pool_pump_mode_callback(self, entity, attribute, old, new, kwargs):
        self.log(f"pool pump mode old: {old} new: {new}")

    def temperature_solar_panel_callback(self, entity, attribute, old, new, kwargs):
        self.log(f"temperature solar panel old: {old} new: {new}")
        inttemp = float(new)
        if (inttemp > 45.0):
            self.turn_on(self.args[KEY_PUMP_SWITCH])
        elif (inttemp < 25.0):
            self.turn_off(self.args[KEY_PUMP_SWITCH])

    def button_callback(self, entity, attribute, old, new, kwargs):
        __switch_state = self.get_state(self.args[KEY_PUMP_SWITCH], attribute="state")
        self.log(f"pool button callback {entity} state: {__switch_state}, first run: {self._firstRun}")
        if (self._firstRun==False):            
            if (__switch_state=="on"):
                self.__pump_pool_on(False)
            else:
                self.__pump_pool_on(True)
        else:
            self._firstRun = False
            self.__pump_pool_on(False)
            self.log(f"first run pool button callback {entity} state: {__switch_state}")
    

