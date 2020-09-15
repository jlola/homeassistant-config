'''
Created on Sep 14, 2020

@author: pc
'''
from abc import ABC

class IModifiedModbusHub(ABC):
    '''
    interface for modbus
    '''
    def getHoldings(self,address,offset:int,count,timeoutMs=50):
        pass
    
    @property
    def ConfigName(self):
        pass