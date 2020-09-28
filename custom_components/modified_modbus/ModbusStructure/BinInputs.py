'''
Created on Sep 13, 2020

@author: pc
'''
from pickletools import uint1,uint2
from builtins import staticmethod

class BinInput(object):
    '''
    binnary inputs
    '''

    def __init__(self,offset):
        '''
        Constructor
        '''
        self.offset = offset
        self.pinNumber:uint1 = 0
        self.value:bool = False
        self.quality:bool = False
        self.latch:bool = False
        self.latchDirection = False
        self.valueOn = 0
        self.valueOff = 0
    
    @staticmethod
    def HoldingsSize() -> uint1:
        '''
        Size of inputs struct in bytes
        '''
        return 1
    
    @property
    def Address(self):
        return self.offset
    
    @property
    def PinNumber(self):
        return self.pinNumber
    
    @property
    def ValueOn(self):
        return self.valueOn
    
    @property
    def ValueOff(self):
        return self.valueOff
        
    def Parse(self,data:uint2):        
        self.pinNumber = 0xFF & data
        self.valueOn = data | 0x0100
        self.valueOff = data & 0xFEFF
    
        
        
        