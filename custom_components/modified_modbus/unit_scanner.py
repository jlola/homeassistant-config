from .ModbusStructure.Header import Header
from .ModbusStructure.TypeDefs import TypeDefs
from .ModbusStructure.TypeDefs import ETypes
from .ModbusStructure.BinInputs import BinInput
from .IModifiedModbusHub import IModifiedModbusHub
import yaml
#import pydevd

class UnitScanner(object):
    def __init__(self, hub:IModifiedModbusHub):
        self._hub = hub

    def Scan(self,slave):
        #pydevd.settrace("192.168.89.25", port=5678)
        h = Header()
        holdings = self._hub.getHoldings(slave,0,10)
        h.Parse(holdings)
        
        holdings = self._hub.getHoldings(slave,0,h.LastIndex)

        typeIndex = 0
        while(typeIndex < h.CountOfTypes):
            startIndex = h.TypesOffset()+TypeDefs.Size()*typeIndex
            typedefsData = holdings[startIndex:startIndex+TypeDefs.Size()]
            typedefs = TypeDefs()
            typedefs.Parse(typedefsData)
            
            if (typedefs.Type == ETypes.BinInputs):
                inputs = self.ParseInputs(holdings, typedefs)
                self.GenerateInputConfig(inputs, slave)            
            typeIndex += 1

    def GenerateInputConfig(self,inputs:list,slave):
#         binary_sensor:
#           - platform: modified_modbus
#             holdings:
#               - name: Sensor1
#                 hub: default
#                 slave: 4
#                 address: 100
#                 value_on: 1254
#                 value_off: 158
        sensors = []
        for binput in inputs:            
            sensor = {
                "platform" : "modified_modbus",                 
                "holdings" : [
                     { "name" : f"binary_sensor{slave}.{binput.PinNumber}",
                       "hub" : self._hub.ConfigName(),
                       "slave" : slave,
                      "address" : binput.Address,
                     "value_on" : binput.ValueOn,
                     "value_off" : binput.ValueOff
                     }
                ],                
            }
            sensors.append(sensor)
            
        dictf = {"binary_sensor" : sensors}
            
        with open(r'bin_sensor.yaml', 'w') as file:
            documents = yaml.dump(dictf, file)

    def ParseInputs(self,holdings:list, typedefs:TypeDefs)->list:
        inputs:list = []
        inputsData = holdings[typedefs.OffsetOfType:typedefs.OffsetOfType+typedefs.Count]            
        typedefIndex = 0 
        while typedefIndex < typedefs.Count:
            binput = BinInput(typedefs.OffsetOfType+typedefIndex)
            binput.Parse(inputsData[typedefIndex])
            inputs.append(binput)
            typedefIndex+=1
        return inputs
    
        


