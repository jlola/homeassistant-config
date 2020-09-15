'''
Created on Aug 27, 2020

@author: pc
'''
from builtins import bool
from ctypes import *
from sys import byteorder
import threading
import time

from interface import implements

from .IDeviceEventConsumer import IDeviceEventConsumer
from .ISerialReceiver import ISerialReceiver
from .SerialPort import SerialPort
from .Helper import Helper


FUNC_GETHOLDINGS = 0x03
FUNC_SETHOLDING = 0x06
FUNC_EVENT = 0xF8
OFFSET_FUNC = 1
OFFSET_COUNT = 2

class ModifiedModbus(implements(ISerialReceiver)):
    '''
    classdocs
    '''

    def __init__(self,port:str,speed:int):
        '''
        Constructor
        '''        
        self.serial = SerialPort(port,speed)
        self.serial.SetReceiver(self)
        self.getholdingsBuffer = []
        self.event = threading.Event()        
        self.receiving = False
        self.buffer = []
        self.consumers = []
        self.lock = threading.RLock()
        self.locked = False
    
    def Open(self):
        self.serial.Open()
        
    def AddConsumer(self,consumer:IDeviceEventConsumer):
        self.consumers.append(consumer)  

    def ThreadNotifyConsumer(self,c):
        c.FireEvent(self.buffer[0])
        
    def OnData(self, data:list):
        self.receiving = True;               

        #strdata = StringBuilder::join(data," ");
        #logger.Trace("Received: %s",strdata.c_str());

        for i in data:    
            self.buffer.append(i);
            completed,isvalid,func = self.DataCompleted(self.buffer)
            if (completed):        
                if (self.locked and func!=FUNC_EVENT):            
                    for c in self.buffer:                
                        self.getholdingsBuffer.append(c);                
                    
                    self.buffer.clear();                
                    self.event.set()            
                elif (func==FUNC_EVENT):            
                    if (not self.checkFrameCrc(self.buffer)):                
                        #string strbuffer = StringBuilder::join(buffer," ");
                        #logger.Error("Received wrong CRC data : %s",strbuffer.c_str());
                        break;                
                    else:                
                        #//fire event on consumers   
                        for c in self.consumers:
                            th = threading.Thread(target=self.ThreadNotifyConsumer,args=(c,))
                            th.start()
                            
                            
                        self.buffer.clear()
                                        
                else:            
                    #string strbuffer = StringBuilder::join(buffer," ");
                    #logger.Error("Completed lost data: %s",strbuffer.c_str());
                    self.buffer.clear();
                    
            elif (not isvalid):        
                #string strbuffer = StringBuilder::join(buffer," ");
                #logger.Error("Invalid lost data: %s",strbuffer.c_str());
                self.buffer.clear();
                break;        
        
        self.receiving = False;
        
    def checkFrameCrc(self,p:bytes):
    #// Enable CRC clock
        length = len(p)
        crc0 = self.CalculateCRC(p[:-2]);
        crc1 = p[length - 2] | (p[length - 1] << 8);
        return crc0 == crc1;        

    def CalculateCRC(self,data):
        '''
        CRC-16-ModBus Algorithm
        '''
        data = bytearray(data)
        poly = 0xA001
        crc = 0xFFFF
        for b in data:
            crc ^= (0xFF & b)
            for _ in range(0, 8):
                if (crc & 0x0001):
                    crc = ((crc >> 1) & 0xFFFF) ^ poly
                else:
                    crc = ((crc >> 1) & 0xFFFF)
    
        return crc & 0xFFFF
    
    def DataCompleted(self,data):
        valid = True
        completed = False
        func = 0
        if (len(data) > OFFSET_COUNT):    
            func = data[OFFSET_FUNC];
            if (func==FUNC_GETHOLDINGS or func==FUNC_EVENT):        
                #/*addr + func + countValue+count+2crc*/
                totalCount = 3 + data[OFFSET_COUNT] + 2;
                if (len(data) > totalCount):
                    valid = False;
                completed = len(data) == totalCount;        
            elif (data[OFFSET_FUNC]==FUNC_SETHOLDING):        
                totalCount = 8;#/*addr + func + firsthi + firstlo+valueHI+valueLow+2crc*/
                if (len(data) > totalCount):
                    valid = False;
                completed = len(data) == totalCount;        
            else:        
                    valid = False;
            
        return completed, valid, func;        
         
    def Send(self, data:bytes,timeoutMs:int = 100) -> bool:
        self.getholdingsBuffer.clear()        
        if (self.event.isSet()):
            self.event.clear()
        self.serial.Write(data)
        timeoutSec  =timeoutMs/1000.0
        signaled = self.event.wait(timeoutSec)        
        return signaled
    
    def Close(self):
        self.serial.Close()
        
    def AppendCRC(self,data):
        datawithoutcrc = bytes(data)
        crc = self.CalculateCRC(datawithoutcrc)
        crcbytes = crc.to_bytes(2,byteorder='big')    
        data.append(crcbytes[1])#swapped
        data.append(crcbytes[0])
        data = bytes(data)
        return data
        
    def getHoldings(self,address,offset:int,count,timeoutMs=50):        
        bufferbytes = bytes(0)
        errormsg = ""
        try:                    
            while(self.receiving):
                time.sleep(1/1000.0)#1ms                            
    
            self.lock.acquire()
            self.locked = True            
            data = []            
            data.append(address)
            data.append(FUNC_GETHOLDINGS)
            offsetbytes = offset.to_bytes(2,byteorder='big')            
            data.append(offsetbytes[0])#swapped
            data.append(offsetbytes[1])
            countbytes = count.to_bytes(2,byteorder='big')                                    
            data.append(countbytes[0])#swapped
            data.append(countbytes[1])
            
            data = self.AppendCRC(data)
            
            print("sended: ",data.hex())
                        
            #logger.Trace("getHoldings: %d, offest: %d, count: %d, timeoutMs: %d",
            #            address, offset, count, timeoutMs);
            #auto start = DateTime::Now();
            if (self.Send(data,timeoutMs)):        
                #//check buffer
                if (self.getholdingsBuffer[0]!=address):
                    errormsg = "wrong address Sended: %d, Received: %d".format(address,self.getholdingsBuffer[0]);
                else: 
                    if (self.getholdingsBuffer[1]!=FUNC_GETHOLDINGS):
                        errormsg = "Incorrect function. Request:%d, Response: %d".format(FUNC_GETHOLDINGS, self.getholdingsBuffer[1])
                    else:
                        if (self.getholdingsBuffer[2]!=count*2):
                            errormsg = "Incorrect count of bytes request:%d, response:%d".format(count*2,self.getholdingsBuffer[2]);                        
                        else:
                            if (not self.checkFrameCrc(self.getholdingsBuffer)):
                                errormsg = "incorrect crc";
                            #else:                        
                                                
                                #auto end = DateTime::Now();
                                #auto duration = end - start;
                                #logger.Trace("finished getHoldings: %d, offest: %d, count: %d, seconds: %f",
                                #        address, offset, count, duration);
                                                                                    
            else:        
                if (address!=1 ):
                    errormsg = "timeout";            
                    
            print(errormsg)
            #logger.Error("Error getHoldings: %d, offest: %d, count: %d, timeoutMs: %d, error: %s",
            #        address, offset, count, timeoutMs, errormsg.c_str());
                        
            bufferbytes = bytes(self.getholdingsBuffer[3:-2])
            holdings = Helper.convertBytesToHoldings(bufferbytes)
            Helper.printHoldings(holdings)
            return bufferbytes
        except Exception as inst:
            print(inst.args) 
            raise inst           
        finally:
            self.locked = False
            self.lock.release()
        
        raise Exception(errormsg);
    
    def setHolding(self,address,offset, val):

        #HisLock lock(modbusmutex);
        errormsg="";        
        try:  

            while(self.receiving):
                time.sleep(1/1000.0)#1ms
            
            self.lock.acquire()
            self.locked = True    
            
            timeoutMs = 200;
            data = []
            data.append(address)
            data.append(FUNC_SETHOLDING)
            offsetbytes = offset.to_bytes(2,byteorder='big')            
            data.append(offsetbytes[0])
            data.append(offsetbytes[1])
            valuebytes = val.to_bytes(2,byteorder='big')
            data.append(valuebytes[0])
            data.append(valuebytes[1])
            
            data = self.AppendCRC(data)
            print("sended: ",data.hex())                            
    
            #logger.Trace("SetHolding: %d, offset: %d, value: %d, timeout: %d",address, offset, val, timeoutMs);
    
            if (self.Send(data,timeoutMs)):    
                respAddress = self.getholdingsBuffer[0];
                if (respAddress == address):            
                    if (data[6] == self.getholdingsBuffer[6] and 
                        data[7] == self.getholdingsBuffer[7]):
                        print("received: ",bytes(self.getholdingsBuffer).hex())
                        return True;
                        
                    else:
                        errormsg = "wrong CRC";
            
                else:
                    errormsg = "wrong response address";                
            else:
                errormsg = "timeout";
        finally:
            self.locked = False
            self.lock.release()
            

        
        #logger.Error("Error setHolding: %d, offset: %d, value: %d, timeoutMs: %d error: %s",
        #address, offset, val, timeoutMs, errormsg.c_str());
        #print("Error setHolding: %d, offset: %d, value: %d, timeoutMs: %d error: %s")        
        raise Exception(errormsg)

    
        