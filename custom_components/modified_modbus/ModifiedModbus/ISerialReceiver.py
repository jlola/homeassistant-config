'''
Created on Aug 25, 2020

@author: pc
'''

from abc import ABC


class ISerialReceiver(ABC):
    '''
    classdocs
    '''    
    def OnData(self, data:list):
        pass
        