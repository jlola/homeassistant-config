from .Header import Header
from .TypeDefs import TypeDefs
from .TypeDefs import ETypes
from .BinInputs import BinInput
from ..IModifiedModbusHub import IModifiedModbusHub
import pydevd

class UnitScanner(object):
    def __init__(self, hub:IModifiedModbusHub):
        self._hub = hub

    def Scan(self,adderss):
        pydevd.settrace("192.168.89.25", port=5678)
        h = Header()
        holdings = self._hub.getHoldings(adderss,0,10)
        h.Parse(holdings)
        
        holdings = self._hub.getHoldings(adderss,0,h.LastIndex)

        typeIndex = 0
        while(typeIndex < h.CountOfTypes):
            startIndex = h.TypesOffset()+TypeDefs.Size()*typeIndex
            typedefsData = holdings[startIndex:startIndex+TypeDefs.Size()]
            typedefs = TypeDefs()
            typedefs.Parse(typedefsData)
            
            if (typedefs.Type == ETypes.BinInputs):
                inputs = self.ParseInpust(holdings, typedefs)
                self.GenerateInputConfig(inputs)            
            typeIndex += 1

    def GenerateInputConfig(self,inputs:BinInput):
        pass

    def ParseInpust(self,holdings:list, typedefs:TypeDefs)->list:
        inputs:list = []
        inputsData = holdings[typedefs.OffsetOfType:typedefs.OffsetOfType+typedefs.Count]            
        typedefIndex = 0 
        while typedefIndex < typedefs.Count:
            binput = BinInput()
            binput.Parse(inputsData[typedefIndex])
            inputs.append(binput)
            typedefIndex+=1
        return inputs
    
        


