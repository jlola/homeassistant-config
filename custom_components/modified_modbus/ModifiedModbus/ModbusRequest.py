'''
Created on Aug 30, 2020

@author: pc
'''

from ctypes import Structure, c_ushort, c_uint8

class ModbusRequest(Structure):
    '''
    
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
        _pack_ = 0
        _fields_ = [("Address", c_uint8),
                    ("Function", c_uint8),
                    ("StartingAddress", c_ushort),
                    ("Count", c_ushort),
                    ("CRC", c_ushort)]
    
    
        