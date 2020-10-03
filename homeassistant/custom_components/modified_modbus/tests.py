'''
Created on Sep 13, 2020

@author: pc
'''
from unittest.mock import Mock
from modified_modbus.ModifiedModbus.Helper import Helper
from modified_modbus.unit_scanner import UnitScanner
from datetime import datetime,timedelta
import threading
import time
from modified_modbus import ModbusCache

x = "0004 0003 000a 0c80 005c 0000 0000 0000 0000 0000 \
     0001 0003 0017 0003 0002 0001 001a 0003 0005 0001 \
     001b 0003 0000 0301 0702 0303 0004 0000 0001 0000 \
     0000 0000 9028 085d 0006 1b00 097f 0001 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000"
byteholdings = bytes.fromhex(x)
holdings = Helper.convertBytesToHoldings(byteholdings)
serial = Mock()

serial.readHoldings = Mock(return_value = holdings)
#serial.getHoldings(4,0,0x005C).return_value = holdings
serial.ConfigName.return_value = "default"

cache = ModbusCache(serial)

#holding = cache.getHoldings(4, 23, 1)

scanner = UnitScanner(serial,4)

print(scanner.GenerateYaml())
temvalue = scanner.GetDS18B20Value("28905d080600001b")
print(temvalue)




    

        