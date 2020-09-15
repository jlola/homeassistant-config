'''
Created on Aug 30, 2020

@author: pc
'''
from abc import ABC


class IDeviceEventConsumer(ABC):
    '''
    object that want to receive events
    '''
    def FireEvent(self,adr:int):
        pass
    
        