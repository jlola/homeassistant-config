'''
Created on Aug 25, 2020

@author: pc
'''

from interface import Interface

class ISerialReceiver(Interface):
    '''
    classdocs
    '''    
    def OnData(self, data:list):
        pass
        