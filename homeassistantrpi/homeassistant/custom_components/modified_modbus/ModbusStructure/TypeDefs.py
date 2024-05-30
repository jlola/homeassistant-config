'''
Created on Sep 13, 2020

@author: pc
'''
from enum import Enum
from pickletools import uint2

class ETypes(Enum):
    Unknown=0
    BinInputs=1
    BinOutputs=2
    AInputs=3
    AOutputs=4
    DS18B20Temp=5
    RFID=6    
    
class EModbusFunc(Enum):
    Unknown = 0
    ReadCoil=1
    ReadDiscreteInput=2
    ReadHoldingRegisters=3
    ReadInputRegisters=4
    WriteCoil=5
    
OFFSET_TYPE = 0
OFFSET_COUNT = 1
OFFSET_OFFSETOFTYPE = 2
OFFSET_MODBUSFUNC = 3

class TypeDefs(object):    
    '''
    types in holdings
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self._type:ETypes = ETypes.Unknown 
        self._count = 0;
        self._offsetOfType = 0;
        self._func:EModbusFunc = EModbusFunc.Unknown
    
    @staticmethod    
    def Size():
        '''
        length in holdings (uint16)
        '''
        return 4
        
    def Parse(self,data:list):
        self._type = ETypes(data[OFFSET_TYPE])
        self._count = data[OFFSET_COUNT]
        self._offsetOfType = data[OFFSET_OFFSETOFTYPE]
        self._func = EModbusFunc(data[OFFSET_MODBUSFUNC])
        
    @property
    def Type(self) -> ETypes:
        return self._type
    
    @property
    def ModbusFunc(self) -> EModbusFunc:
        return self._func
    
    @property
    def Count(self):
        return self._count
    
    @property
    def OffsetOfType(self):
        return self._offsetOfType
    
        
        