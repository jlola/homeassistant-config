'''
Created on Aug 30, 2020

@author: pc
'''
from interface import Interface

class IDeviceEventConsumer(Interface):
    '''
    object that want to receive events
    '''
    def FireEvent(self,adr:int):
        pass
    
        