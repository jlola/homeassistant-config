'''
Created on Aug 25, 2020

@author: pc
'''

from abc import ABC

from interface import Interface


class ISerialReceiver(Interface):
    '''
    classdocs
    '''    
    def OnData(self, data:list):
        pass
        