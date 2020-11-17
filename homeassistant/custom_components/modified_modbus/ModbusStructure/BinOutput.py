'''
Created on Sep 30, 2020

@author: pc
'''
from pickletools import uint1



class BinOutput(object):
    '''
    binary output
    '''


    def __init__(self,hub,slave, offset):
        '''
        Constructor
        '''
        self._slave = slave        
        self._hub = hub        
        self._offset = offset
        self._pinNumber = 0
        self._value:bool = False
        self._quality:bool = False            
        self._valueOn = 0
        self._valueOff = 0
        self._name = f"switch.{self._slave}.{self._pinNumber}"
    
    def Parse(self,holdings):
        data = holdings[self._offset]        
        self._pinNumber = 0xFF & data
        self._valueOn = data | 0x0100
        self._valueOff = data & 0xFEFF
        
    def SetValues(self,valueOn,valueOff, name):
        self._valueOn = valueOn
        self._valueOff = valueOff
        self._name = name
        
    @property
    def Offset(self):
        return self._offset
    
    @property
    def ValueOn(self):
        return self._valueOn
    
    @property
    def ValueOff(self):
        return self._valueOff
    
    @staticmethod
    def HoldingsSize()->uint1:
        return 1
    
    def GenerateYaml(self):        
# switch:
# - holdings:  
#   - hub: default
#     name: myswitch
#     slave: 4
#    offset: 26
#    command_on: 260
#    command_off: 4
#    state_on: 260
#    state_off: 4
#    verify_state: False
#  platform: modified_modbus
                    
        outputyaml = {
            "platform" : "modified_modbus",                 
            "holdings" : [
                { 
                "name" : self._name,
                "hub" : self._hub.ConfigName,
                "slave" : self._slave,
                "offset" : self.Offset,
                 "command_on" : self.ValueOn,
                 "command_off" : self.ValueOff,
                 "state_on" : self.ValueOn,
                 "state_off" : self.ValueOff
                 }
            ],                
        }
        
        return outputyaml    
    