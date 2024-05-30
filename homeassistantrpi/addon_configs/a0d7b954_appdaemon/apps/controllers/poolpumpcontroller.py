import hassapi as hass

KEY_PUMP_SWITCH = "pool_pump_switch"
KEY_POOL_PUMP_BUTTON = "pool_pump_button"

#pool_pump_controller:
#  module: PoolPumpController
#  pool_pump_switch: switch.switch_7_7_pool_pump
#  pool_pump_button: binary_input.binary_sensor_7_1_pool_pump_button

# Declare Class
class PoolPumpController(hass.Hass):
    def initialize(self):
        self.listen_state(self.button_callback, self.args[KEY_POOL_PUMP_BUTTON], attribute = "state")        
        self._firstRun = True

    def __pump_pool_on(self,run):
        self.log(f"__pump_pool_on run:{run}") 
        if (run==True):
            self.turn_on(self.args[KEY_PUMP_SWITCH])
        else:
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
