'''
Created on Sep 14, 2020

@author: pc
'''
from abc import ABC
from pickletools import uint2

class IModifiedModbusHub(ABC):
    '''
    interface for modbus
    '''
    def readHoldings(self,slave:int,offset:int,count:int, timeout:int=50):
        pass
    
    def readHolding(self,slave:int,offset:int)->uint2:
        pass
    
    def writeHolding(self,slave:int,offset:int,value:uint2):
        pass
    
    @property
    def ConfigName(self):
        pass