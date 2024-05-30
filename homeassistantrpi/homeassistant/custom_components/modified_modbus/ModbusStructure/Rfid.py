'''
Created on Nov 8, 2020

@author: pc
'''
from pickletools import uint1
from .BinOutput import BinOutput
from ..const import CONF_STRING,CONF_HOLDINGS_TYPE
class Rfid():
    '''
    rfid
    '''
    
    OFFSET_NEWDATA = 0
    OFFSET_RFID = 1
    RFID_HOLDINGS_LEN = 25
    
    def __init__(self,hub, slave, offset):
        '''
        Constructor
        '''
        self._hub = hub
        self.slave = slave
        self.offset = offset
        self.rfid = ""
        
    @staticmethod
    def HoldingsSize() -> uint1:
        '''
        Size of inputs struct in bytes
        '''
        return 26
    
    @property
    def Offset(self):
        return self.offset
    
    def Parse(self,holdings):            
        self.rfid = "".join(map(chr, holdings[self.offset + self.OFFSET_RFID:self.RFID_HOLDINGS_LEN]))
        
    @property
    def RFIDValue(self):
        return self.rfid
    
    def GenerateYaml(self):
        sensor = {
            "platform" : "modified_modbus",                 
            "holdings" : [
                 { 
                   "name" : f"rfidreader_{self.slave}",
                   "hub" : self._hub.ConfigName,
                   CONF_HOLDINGS_TYPE : CONF_STRING,
                   "slave" : self.slave,
                   "offset" : self.Offset+self.OFFSET_RFID,
                   "count" : self.RFID_HOLDINGS_LEN                                                                          
                 }
            ],                
        }        
        
        return sensor
    
    def GenerateYamlReset(self):
        binOutput = BinOutput(self._hub,self.slave, self.offset+self.OFFSET_NEWDATA)
        binOutput.SetValues(1, 0, f"rfidreader_reset_{self.slave}")
        return binOutput.GenerateYaml()
        
        