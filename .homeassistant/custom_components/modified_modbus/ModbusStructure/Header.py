'''
Created on Sep 13, 2020

@author: pc
'''
from pickletools import uint2
from .. import DEVADDR_OFFSET, COUNT_OF_TYPES_OFFSET,\
    TYPE_DEFS_OFFSET, RESET_REG_OFFSET, LAST_INDEX


class Header(object):
    '''
    header of items, contains informations about count of items and their positions
    '''
    DEVICEBASE =                     0
    DEVADDR_OFFSET =                 DEVICEBASE+0
    COUNT_OF_TYPES_OFFSET =          DEVICEBASE+1
    TYPE_DEFS_OFFSET =               DEVICEBASE+2
    RESET_REG_OFFSET =               DEVICEBASE+3
    LAST_INDEX =                     DEVICEBASE+4
    CHANGE_FLAG =                    DEVICEBASE+5

    def __init__(self ):
        '''        
        '''
        self._modbusAddress = 0
        self._countOfTypes = 0;
        self._typeDefsOffset = 0;
        self._resetReg = 0;
        self._lastIndex = 0;
    
    def Parse(self, data:list):
        self._modbusAddress = data[DEVADDR_OFFSET]
        self._countOfTypes = data[COUNT_OF_TYPES_OFFSET]
        self._typeDefsOffset = data[TYPE_DEFS_OFFSET]
        self._resetReg = data[RESET_REG_OFFSET]
        self._lastIndex = data[LAST_INDEX]
    
    @property
    def CountOfTypes(self):
        return self._countOfTypes
    
    @property
    def LastIndex(self):
        return self._lastIndex
    
    @property
    def ModbusAddress(self) -> uint2:
        """Address of unit."""
        return self._modbusAddress
    
    def TypesOffset(self) -> uint2:
        return self._typeDefsOffset
    