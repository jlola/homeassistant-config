'''
Created on Sep 13, 2020

@author: pc
'''
from unittest.mock import Mock,PropertyMock
from modified_modbus.ModifiedModbus.Helper import Helper
from modified_modbus.unit_scanner import UnitScanner
from datetime import datetime,timedelta
import threading
import time
from modified_modbus import ModbusCache
from modified_modbus.ModifiedModbus.ISerialReceiver import ISerialReceiver
from modified_modbus.ModbusStructure.BinInput import BinInput

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
     
y = "0008 0004 000a 0c80 0078 0000 0000 0000 0000 0000 \
     0002 0001 001b 0003 0001 0001 001c 0003 0005 0001 \
     001d 0003 0006 0001 005e 0003 0000 0003 0702 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0001 3002 3630 4534 4132 0d34 \
     030a 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000"
     
     
lukasTeploty = "\
     0002 0003 000a 0c80 005a 0000 0000 0000 0000 0000 \
     0001 0001 0017 0003 0002 0001 0018 0003 0005 0001 \
     0019 0003 0000 0301 0004 0001 0004 0000 0000 0000 \
     ee28 6ada 162e 3401 0627 0001 ee28 2ca6 1613 bd02 \
     090e 0001 ee28 3041 1613 1c02 ffce 0001 ee28 072d \
     1616 3501 0765 0001 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
     0000 0000 0000 0000 0000 0000 0000 0000 0000 0000"
     
byteholdings = bytes.fromhex(lukasTeploty)
holdings = Helper.convertBytesToHoldings(byteholdings)
serial = Mock()

serial.readHoldings = Mock(return_value = holdings)
mock_ConfigName = PropertyMock(return_value='default')
#serial.getHoldings(4,0,0x005C).return_value = holdings
type(serial).ConfigName = mock_ConfigName

cache = ModbusCache(serial)

#holding = cache.getHoldings(4, 23, 1)

scanner = UnitScanner(serial,2)

print(scanner.GenerateYaml())
temvalue = scanner.GetDS18B20Value("28eeda6a2e160134")
print(temvalue)
temvalue = scanner.GetDS18B20Value("28eea62c131602bd")
print(temvalue)
temvalue = scanner.GetDS18B20Value("28ee41301316021c")
print(temvalue)
temvalue = scanner.GetDS18B20Value("28ee2d0716160135")
print(temvalue)


value = 1539
print(Helper.BitValue(value, 8))
value = 1795
print(Helper.BitValue(value, 8))



    

        