import appdaemon.plugins.hass.hassapi as hass

class HeaterController(hass.Hass):
    def initialize(self):
        self.log("Floor heater starting")
        self.__temperature = self.args["temperature"]
        self.__servo_time = self.args["servotime"]
        self.__setpoint = self.args["setpoint"]
        self.__thermostatinput = self.args["thremostatinput"]