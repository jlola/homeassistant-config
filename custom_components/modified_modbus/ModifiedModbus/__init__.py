'''
Created on Aug 27, 2020

@author: pc
'''
from builtins import bool
from ctypes import *
from sys import byteorder
import threading
import logging

from .IDeviceEventConsumer import IDeviceEventConsumer
from .ISerialReceiver import ISerialReceiver
from .SerialPort import SerialPort
from .SocketClient import SocketClient
from .Helper import Helper
import time
logger = logging.getLogger(__name__)

FUNC_GETHOLDINGS = 0x03
FUNC_SETHOLDING = 0x06
FUNC_EVENT = 0xF8
OFFSET_FUNC = 1
OFFSET_COUNT = 2

class ModifiedModbus(ISerialReceiver):
    '''
    classdocs
    '''

    def __init__(self,serial):
        '''
        Constructor
        '''
        self.serial =  serial
        self.serial.SetReceiver(self)
        self.getholdingsBuffer = []
        self.event = threading.Event()
        self.receiving = False
        self.buffer = []
        self.consumers = []
        self.lock = threading.Lock()
        self.locked = False

    def Open(self):
        self.serial.Open()
        
    def AddConsumer(self,consumer:IDeviceEventConsumer):
        self.consumers.append(consumer)  

    def ThreadNotifyConsumer(self,c,adr):
        try:
            c.FireEvent(adr)
        except Exception as inst:
            logger.info(f"ThreadNotifyConsumer({adr}) exception: {inst.args}");
        
    def OnData(self, data:list):
        self.receiving = True;               

        #strdata = StringBuilder::join(data," ");
        
        bts = bytes(data)
        logger.info(f"Received OnData: {bts.hex()}");        

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
                        #crcErrorbuf = bytes(self.buffer)
                        #logger.error(f"Received wrong CRC data : {crcErrorbuf.hex()}")
                        break
                    else:                
                        #fire event on consumers
                        adr = self.buffer[0]
                        logger.info(f"Fired F8 event on adress: {adr}")
                        for c in self.consumers:
                            th = threading.Thread(target=self.ThreadNotifyConsumer,args=(c,adr))
                            th.start()
                            
                    self.buffer.clear()
                else:            
                    #lostdata = bytes(self.buffer)
                    #logger.error(f"Completed lost data: {lostdata.hex()}")
                    self.buffer.clear();
            elif (not isvalid):        
                #notvaliddata = bytes(self.buffer)
                #logger.error(f"Invalid lost data: {notvaliddata.hex()}")
                self.buffer.clear()
                break
        
        self.receiving = False
        
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
        self.buffer.clear()
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
        
    def getHoldings(self,slave,offset:int,count,timeoutMs=50):        
        
        errormsg = ""
        
        while(self.receiving):
            time.sleep(0.001)#1ms                 
        self.lock.acquire()
        self.locked = True                               
        attempt = 0
        
        try:                    
            while(attempt < 3):                
                attempt += 1
                bufferbytes = bytes(0)
                errormsg = f"getHoldings type:{self.serial.GetName()}, slave:{slave},offset: {offset} count: {count}, attepmt:{attempt} \n"
                data = []            
                data.append(slave)
                data.append(FUNC_GETHOLDINGS)
                offsetbytes = offset.to_bytes(2,byteorder='big')            
                data.append(offsetbytes[0])#swapped
                data.append(offsetbytes[1])
                countbytes = count.to_bytes(2,byteorder='big')                                    
                data.append(countbytes[0])#swapped
                data.append(countbytes[1])
                
                data = self.AppendCRC(data)
                
                errormsg += f"sended: {data.hex()}\n"
                            
                logger.info(f"getHoldings: slave: {slave}, offest: {offset}, count: {count}, timeoutMs: {timeoutMs}")
                logger.info(f"SendedData: {data.hex()}")
                #auto start = DateTime::Now();
                if (self.Send(data,timeoutMs)):        
                    #//check buffer
                    if (self.getholdingsBuffer[0]!=slave):
                        errormsg += f"wrong address Sended: {slave}, Received: {self.getholdingsBuffer[0]}";
                    elif (self.getholdingsBuffer[1]!=FUNC_GETHOLDINGS):
                        errormsg += f"Incorrect function. Request:{FUNC_GETHOLDINGS}, Response: {self.getholdingsBuffer[1]}"
                    elif (self.getholdingsBuffer[2]!=count*2):
                        errormsg += f"Incorrect count of bytes request:{count*2}, response:{self.getholdingsBuffer[2]}"
                    elif (not self.checkFrameCrc(self.getholdingsBuffer)):
                        errormsg += "incorrect crc";
                                #else:                        
                                                    
                                    #auto end = DateTime::Now();
                                    #auto duration = end - start;
                                    #logger.Trace("finished getHoldings: %d, offest: %d, count: %d, seconds: %f",
                                    #        address, offset, count, duration);
                    else:
                        bufferbytes = bytes(self.getholdingsBuffer[3:-2])
                        holdings = Helper.convertBytesToHoldings(bufferbytes)
                        Helper.printHoldings(holdings)
                        return holdings
                                                                                        
                else:        
                    if (slave!=1 ):
                        errormsg += " timeout";            
                
                errormsg += f" attempt: {attempt}"
                #print(errormsg)
                logger.error("Error getHoldings: %d, offest: %d, count: %d, timeoutMs: %d, error: %s",
                        slave, offset, count, timeoutMs, errormsg)
                time.sleep(0.05)
            
        except Exception as inst:
            print(inst.args) 
            raise inst           
        finally:
            self.locked = False
            self.lock.release()

        time.sleep(1)
        raise Exception(errormsg);
    
    def setHolding(self,slave,offset, val):

        #HisLock lock(modbusmutex);
             
        attempt = 0
        while(self.receiving):
            time.sleep(1/1000.0)#1ms
        self.lock.acquire()
        self.locked = True 
        try:                    
            while(attempt < 3):                
                attempt += 1 
                errormsg = f"setHolding slave:{slave},offset: {offset} attempt: {attempt} -> \
                "
                timeoutMs = 200;
                data = []
                data.append(slave)
                data.append(FUNC_SETHOLDING)
                offsetbytes = offset.to_bytes(2,byteorder='big')            
                data.append(offsetbytes[0])
                data.append(offsetbytes[1])
                valuebytes = val.to_bytes(2,byteorder='big')
                data.append(valuebytes[0])
                data.append(valuebytes[1])
                
                data = self.AppendCRC(data)
                        
                logger.info("SetHolding: %d, offset: %d, value: %d, timeout: %d",slave, offset, val, timeoutMs);
                logger.info(f"SendedData: {data.hex()}")
                if (self.Send(data,timeoutMs)):    
                    respAddress = self.getholdingsBuffer[0];
                    if (respAddress == slave):            
                        if (data[6] == self.getholdingsBuffer[6] and 
                            data[7] == self.getholdingsBuffer[7]):
                            errormsg += "received: " + bytes(self.getholdingsBuffer).hex()
                            return True;
                            
                        else:
                            errormsg += f"wrong CRC, slave: {slave}";
                
                    else:
                        errormsg += f"wrong response address, slave: {slave}";                
                else:
                    errormsg += f", timeout {slave}";
                errormsg += f", attempt: {attempt}"                
                time.sleep(0.05)
        finally:
            self.locked = False
            self.lock.release()
            

        time.sleep(1)
        #logger.Error("Error setHolding: %d, offset: %d, value: %d, timeoutMs: %d error: %s",
        #address, offset, val, timeoutMs, errormsg.c_str());
        #print("Error setHolding: %d, offset: %d, value: %d, timeoutMs: %d error: %s")        
        raise Exception(errormsg)

    
        