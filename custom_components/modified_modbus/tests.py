'''
Created on Sep 13, 2020

@author: pc
'''
from unittest.mock import Mock
from .ModifiedModbus.Helper import Helper
from .unit_scanner import UnitScanner

x = "0004 0003 000a 0c80 005c 0000 0000 0000 0000 0000 0001 0003 0017 0003 0002 0001 001a 0003 0005 0001 001b 0003 0000 0301 0702 0303 0004 0000 0001 0000 0000 0000 9028 085d 0006 1b00 097f 0001 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000"
byteholdings = bytes.fromhex(x)
holdings = Helper.convertBytesToHoldings(byteholdings)
serial = Mock()

serial.getHoldings.return_value = holdings

scanner = UnitScanner(serial)

scanner.Scan(4,)

        
        
        



    

        