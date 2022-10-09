import hassapi as hass

#real_time_tag

#watchdog_controller:
#   module: watchdogcontroller
#   class: WatchDogController
#   appdaemon_time: input_text.appdaemon_time


class WatchDogController(hass.Hass):
    def initialize(self):
        self.__timer = self.run_every(self.__on_timer, "now", 10)

    def __on_timer(self,kwargs):
        t = self.datetime()
        self.set_state(self.args["appdaemon_time"],state=t)