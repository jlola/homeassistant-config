import hassapi as hass

#real_time_tag

#watchdog_controller:
#   module: watchdogcontroller
#   class: WatchDogController
#   appdaemon_time: input_text.appdaemon_time
#   ups_capacity: waveshare_ups_hat
#   ups_online: input_boolean.ups_online_tester
#   ups_online: sensor.waveshare_ups_hat_online
#   tika periodicky abych videl ze appdaemon zjie
KEY_APPDAEMONTIME = "appdaemon_time"
KEY_UPSONLINE = "ups_online"

class WatchDogController(hass.Hass):
    def initialize(self):
        self.__timer = self.run_every(self.__on_timer, "now", 10) #run every 10s
        self.listen_state(self.ups_online_callback, self.args[KEY_UPSONLINE], attribute = "state")
        self.shutdown_seconds = -1
        self.count_down_run = False

    def ups_online_callback(self, entity, attribute, old, new, kwargs):
        self.log(f"is ups online: {self.is_ups_online()}")
        if (self.is_ups_online()):
            self.count_down_run = False
        else:
            self.count_down_run = True
            self.shutdown_seconds = 300

    def __on_timer(self,kwargs):
        t = self.datetime()
                
        if (self.count_down_run==True):
            self.shutdown_seconds -= 10
            self.set_state(self.args[KEY_APPDAEMONTIME],state=self.shutdown_seconds)
            self.log(f"Seconds to shut down: {self.shutdown_seconds}")
            if (self.shutdown_seconds==0):
                self.count_down_run = False
                self.shutdown()
        else:
            self.set_state(self.args[KEY_APPDAEMONTIME],state=t)
    
    def is_ups_online(self):
        return self.get_state(self.args["ups_online"], attribute="state")=="on"

    def shutdown(self):
        self.log(f"Shutting down long time power off")
        self.set_state(self.args[KEY_APPDAEMONTIME],state="Shutdown")
        self.call_service("hassio")