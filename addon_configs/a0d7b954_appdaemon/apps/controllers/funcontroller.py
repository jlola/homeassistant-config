import hassapi as hass

class FunController(hass.Hass):
    def initialize(self):
        self.timer = None
        self.fun_button = self.args["fan_button"]
        self.fun_switch = self.args["fan_switch"]
        self.listen_state(self.on_button_pressed, self.fun_button, new="off") 
        self.listen_state(self.on_switch_changed, self.fun_switch, new="on") 

    def on_button_pressed(self, entity, attribute, old, new, kwargs):
        if (self.get_state(self.fun_button)=="off"):
            if (self.get_state(self.fun_switch)=="off"):
                self.enable_fun(True)
                self.__start_timer()
            else:
                self.enable_fun(False)
    
    def on_switch_changed(self, entity, attribute, old, new, kwargs):
        if (self.get_state(self.fun_button)=="on"):
            if (self.get_state(self.fun_switch)=="off"):
                self.enable_fun(True)                            
        self.__start_timer()


    def __start_timer(self):        
        if (self.timer != None):
            self.cancel_timer(self.timer)
        self.timer = self.run_in(self.__on_timer, 300)

    def __on_timer(self, kwargs):
        self.enable_fun(False)
        self._timer = None

    def enable_fun(self,run):
        self.log(f"run:{run}")
        if (run==True):
            self.turn_on(self.fun_switch)
        else:
            self.turn_off(self.fun_switch)




