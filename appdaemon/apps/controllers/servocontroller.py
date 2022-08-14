import hassapi as hass

from enum import Enum
class ServoMode(Enum):
    Stop = 0
    Start = 1
    Reset = 2
SERVO_OPEN_TO_CLOSE_TIME = 120 #seconds
MAX_EQUAL_COUNTER = 2

class ServoController(hass.Hass):
    def initialize(self):
        self.__servo_value = self.args["servo_value"]
        self.__actual_time = self.args["servo_time"]
        self.__mode = ServoMode.Stop
        self.__request_time = 0
        self.__open_switch = self.args["servo_open_switch"]
        self.__close_switch = self.args["servo_close_switch"]
        self.listen_state(self.servo_value_callback, self.__servo_value, attribute = "state")
        self.__timer = None
        self.log(f"Initialized")
        self.__oldpercent = 0
        self.reset()
        self.equalCounter = 0

    def servo_value_callback(self, entity, attribute, old, new, kwargs):
        if (self.__mode == ServoMode.Reset):
            self.log(f"servo_value_callback: value: {new} ignored because resetting")
            return
        newpercent = float(new)
        self.log(f"servo_value_callback: new percent value: {new}")
        if (newpercent > 100):
            newpercent = 100
        elif (newpercent < 0):
            newpercent = 0
        #if (abs(self.__oldpercent-newpercent)>=1):
        self.__request_time = round(newpercent * SERVO_OPEN_TO_CLOSE_TIME / 100,0)
        if (self.__request_time!=self.get_servo_time()):
            self.__mode = ServoMode.Start
            self.__start_timer()


    def __turn(self,switch, run):
        #self.log(f"servo:{switch}, run:{run}")
        if (run==True):
            self.turn_on(switch)
        else:
            self.turn_off(switch)

    def get_servo_time(self):
        return int(float(self.get_state(self.__actual_time, attribute="state")))

    def set_servo_time(self,value):
        return self.set_state(self.__actual_time,state=value)

    def get_servo_value(self):
        return int(float(self.get_state(self.__servo_value, attribute="state")))

    def set_servo_value(self,value):
        return self.set_state(self.__servo_value,state=value)

    def reset(self):
        self.log(f"Reseting...")
        self.__mode = ServoMode.Reset
        self.set_servo_time(SERVO_OPEN_TO_CLOSE_TIME+10)
        self.__request_time = 0
        self.__start_timer()

    def __start_timer(self):
        if (self.__timer == None):
            self.__timer = self.run_every(self.__on_timer, "now", 1)

    def __on_timer(self, kwargs):
        servo_time = self.get_servo_time()
        self.log(f"servo_time:{servo_time}, request_time: {self.__request_time}")
        if (servo_time == self.__request_time):
            self.equalCounter = self.equalCounter + 1
            self.__disable()
            if (self.__timer != None and self.equalCounter==MAX_EQUAL_COUNTER):
                self.cancel_timer(self.__timer)
                self.__timer = None
            if (self.__mode == ServoMode.Reset):
                self.__mode = ServoMode.Stop
                self.set_servo_value(self.get_servo_value())
            else:
                self.__mode = ServoMode.Stop
        elif (self.__request_time > servo_time):
            self.__run_to_open()
            self.set_servo_time(servo_time+1)
            self.equalCounter = 0
        elif (self.__request_time < servo_time):
            self.__run_to_close()
            self.set_servo_time(servo_time-1)
            self.equalCounter = 0

    def __run_to_open(self):
        self.__turn(self.__close_switch,False)
        self.__turn(self.__open_switch,True)

    def __run_to_close(self):
        self.__turn(self.__open_switch,False)
        self.__turn(self.__close_switch,True)

    def __disable(self):
        self.__turn(self.__open_switch,False)
        self.__turn(self.__close_switch,False)



