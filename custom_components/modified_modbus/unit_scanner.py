from .ModbusStructure.Header import Header
from .ModbusStructure.TypeDefs import TypeDefs
from .ModbusStructure.TypeDefs import ETypes
from .ModbusStructure.BinInput import BinInput
from .ModbusStructure.BinOutput import BinOutput
from .IModifiedModbusHub import IModifiedModbusHub
from .ModbusStructure.DS18B20 import OneWireHeader
from .ModbusStructure.Rfid import Rfid
import yaml
import os
from .ModbusStructure.DS18B20 import DS18B20
import logging

_LOGGER = logging.getLogger(__name__)
#import pydevd

class UnitScanner(object):
    def __init__(self, hub:IModifiedModbusHub, slave):
        self._hub = hub
        self._slave = slave
        self._typedefs = None

    def __scan(self):
        _LOGGER.info(f"Scan | Slave: {self._slave} started.")

        self.__read()
        #pydevd.settrace("192.168.89.25", port=5678)        
        _LOGGER.info(f"Scan | Slave: {self._slave} Last index: {self._header.LastIndex}")
        _LOGGER.info(f"Scan | Slave: {self._slave} Started. Detected {len(self._typedefs)} types")

        owtypedef = self.FindTypeDefByType(self._typedefs, ETypes.DS18B20Temp)
        if (owtypedef!=None):
            #_LOGGER.info(f"Scan | Slave: {self._slave} Found owtypedef")
            self._scanOneWire(owtypedef)
            self._holdings = self._hub.readHoldings(self._slave,0,self._header.LastIndex,150)
                        
        return self._holdings
    
    def __read(self):
        self._header = Header()
        self._holdings = self._hub.readHoldings(self._slave,0,10,100)
        self._header.Parse(self._holdings)        
        self._holdings = self._hub.readHoldings(self._slave,0,self._header.LastIndex,150)
        self._typedefs = self.__ParseTypeDefs(self._holdings, self._header)
                
    def GetDS18B20Value(self, owid): 
        self.__read()        
        for typedef in self._typedefs:       
            if (typedef.Type == ETypes.DS18B20Temp):    
                temps = self.__ParseDS18B20(self._holdings, typedef)
                for temp in temps:
                    if (temp.OwId == owid):
                        return temp.Value
        self.__scan() #pokud nic nenajdu zkusim scan
        raise Exception(f"ds18b20: {owid} on slave: {self._slave} desn't exits")
        
    def __ParseTypeDefs(self,holdings, h)->[]:
        typedefs = []
        typeIndex = 0
        while(typeIndex < h.CountOfTypes):
            startIndex = h.TypesOffset()+TypeDefs.Size()*typeIndex
            typedefData = holdings[startIndex:startIndex+TypeDefs.Size()]
            typedef = TypeDefs()
            typedef.Parse(typedefData)
            typedefs.append(typedef)                             
            typeIndex += 1
        return typedefs
                                            
            
    def GenerateYaml(self):
        dictf = {}
        self.__scan()
        for typedef in self._typedefs:        
            if (typedef.Type == ETypes.BinInputs):
                inputs = self.__ParseInputs(self._holdings, typedef)
                self.__GenerateInputConfig(inputs, dictf)
            if (typedef.Type == ETypes.BinOutputs):
                outputs = self.__ParseOutputs(self._holdings, typedef)
                self.__GenerateOutputConfig(outputs, dictf)
            elif (typedef.Type == ETypes.DS18B20Temp):    
                temps = self.__ParseDS18B20(self._holdings, typedef)
                _LOGGER.info(f"Scan | GenerateYaml. Detected {len(temps)} DS18B20s")
                self.__GenerateDS18B20Config(temps,dictf)
            elif (typedef.Type == ETypes.RFID):    
                temps = self.__ParseRFIDs(self._holdings, typedef)
                self.__GenerateRFIDsConfig(temps, dictf)
        
        yamlsdir = f'{os.getcwd()}/scan'
        if not os.path.exists(yamlsdir):
            os.makedirs(yamlsdir)
        
        #write to file
        fileName = f'{yamlsdir}/homeismodule.{self._slave}.yaml'
        with open(fileName, 'w') as file:
            yaml.dump(dictf, file)
        return fileName

    def __GenerateInputConfig(self,inputs:list,dictf:[]):        
        if (len(inputs)==0):
            return
        
        yamlinputs = []
        for binput in inputs:            
            yaml = binput.GenerateYaml()
            yamlinputs.append(yaml)
            
        dictf[f"binary_sensor {self._slave}"] = yamlinputs
    
    def __GenerateOutputConfig(self,outputs:list,dictf:[]):        
        if (len(outputs)==0):
            return
        
        yamlouputs = []
        for boutput in outputs:            
            yaml = boutput.GenerateYaml()
            yamlouputs.append(yaml)
            
        dictf[f"switch {self._slave}"] = yamlouputs
            
    def __ParseOutputs(self, holdings, typedef):
        outputs:list = []
        typedefIndex = 0
        while typedefIndex < typedef.Count:
            offset = typedef.OffsetOfType+typedefIndex*BinOutput.HoldingsSize()
            binoutput = BinOutput(self._hub ,self._slave, offset)
            binoutput.Parse(holdings)
            outputs.append(binoutput)
            typedefIndex+=1
        return outputs

    def __ParseInputs(self, holdings:list, typedef:TypeDefs)->list:
        inputs:list = []                
        typedefIndex = 0 
        while typedefIndex < typedef.Count:
            offset = typedef.OffsetOfType+typedefIndex*BinInput.HoldingsSize()
            binput = BinInput(self._hub ,self._slave, offset)
            binput.Parse(holdings)
            inputs.append(binput)
            typedefIndex+=1
        return inputs
    
    def __ParseRFIDs(self, holdings:list, typedef:TypeDefs)->list:
        rfids:list = []                
        typedefIndex = 0 
        while typedefIndex < typedef.Count:
            offset = typedef.OffsetOfType+typedefIndex*Rfid.HoldingsSize()
            rfid = Rfid(self._hub ,self._slave, offset)
            rfid.Parse(holdings)
            rfids.append(rfid)
            typedefIndex+=1
        return rfids
            
    def __GenerateDS18B20Config(self,ds18b20s:list,dictf:[]):
        if (len(ds18b20s)==0):
            return
        
        sensors = []
        for ds18b20 in ds18b20s:    
            ds18b20yaml = ds18b20.GenerateYaml()                    
            sensors.append(ds18b20yaml)                    
        dictf[f"sensor  {self._slave}"] = sensors
        
        
    def __GenerateRFIDsConfig(self,rfids:list,dictf:{}):
        if (len(rfids)==0):
            return
        sensorskey = f"sensor  {self._slave}"
        switcheskey = f"switch {self._slave}"
        
        rfidsensors = dictf.get(sensorskey,[])        
        switches =  dictf.get(switcheskey,[])
        if (switches==None):
            dictf[switcheskey] = []
            switches = dictf[switcheskey]
        for rfidobj in rfids:    
            rfidobjyaml = rfidobj.GenerateYaml()                    
            rfidsensors.append(rfidobjyaml)
            rfidResetSwitch = rfidobj.GenerateYamlReset()
            switches.append(rfidResetSwitch)
                                    
        dictf[sensorskey] = rfidsensors
        dictf[switcheskey] = switches
    
    '''
    returns: list of ds18b20 structs
    '''       
    
    def FindTypeDefByType(self, typedefs:[],type:ETypes):
        for t in typedefs:
            if (t.Type==type):
                return t
        
        return None
        
    
    def _scanOneWire(self, typedef:TypeDefs):                    
        self._hub.writeHolding(self._slave, typedef.OffsetOfType, 1)
        
    
    def __ParseDS18B20(self,holdings:list, typedefs:TypeDefs):
        temps:list = []        
        typedefIndex = 0        
        owHeader = OneWireHeader(self._slave, typedefs.OffsetOfType)
        owHeader.Parse(holdings)
        while typedefIndex < owHeader.CountDevices:
            offset = owHeader.GetFirstDS18B20Offset()+typedefIndex*DS18B20.HoldingsSize()
            temp = DS18B20(self._hub, self._slave, offset)
            temp.Parse(offset, holdings)
            mstr = temp.OwId            
            temps.append(temp)
            typedefIndex += 1
        return temps
    
        


