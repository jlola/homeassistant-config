'''
Created on May 16, 20222

@author: pc
'''

from abc import ABC
from .ISerialReceiver import ISerialReceiver

class ISerialCommunication(ABC):
    '''
    classdocs
    '''    
    def OnData(self, data:list):
        pass

    def Open(self):
        pass

    def Close(self):
        pass

    def SetReceiver(self, receiver: ISerialReceiver):
        pass

    def Write(self,data:bytes):
        pass

    def Read(self) :
        pass

    