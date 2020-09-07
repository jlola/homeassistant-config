'''
Created on Aug 24, 2020

@author: pc
'''
import threading;
import serial
from enum import Enum
from ModifiedModbus.ISerialReceiver import ISerialReceiver

class State(Enum):
    OPEN=0,
    CLOSE=1

class SerialPort(object):
    '''
    classdocs
    '''
    def __init__(self, port:str, speed: int):
        '''
        Constructor        
        '''
        self.port = port
        self.speed = speed
        self.state = State.CLOSE    
        self.timeoutMs = 0.05
        self.minBytes = 7
            
    
    def Open(self):
        if (self.state == State.OPEN) :
            return
        
        self.serial = serial.Serial(self.port,self.speed,timeout=self.timeoutMs)  # open serial port
        self.state = State.OPEN
        self.thread = threading.Thread(target=self.ThreadMethod)
        self.thread.start()
        
    def Close(self):
        if (self.state == State.CLOSE) :
            return
        self.state = State.CLOSE
        self.serial.close()
               
        
    def SetReceiver(self, receiver: ISerialReceiver):
        self.receiver = receiver
        
    def Write(self,data:bytes):
        if(self.state != State.OPEN):
            raise NameError(" called but state != OPEN. Please call Open() first.")

        
        writeResult = self.serial.write(data);

        # Check status
        if (writeResult == -1) : 
            raise ValueError
        
        return writeResult
                
        
    def Read(self) :    
                
        # Read from file
        # We provide the underlying raw array from the readBuffer_ vector to this C api.
        # This will work because we do not delete/resize the vector while this method
        # is called
        data = self.serial.read(self.minBytes);

        # Error Handling
        if len(data) < 0 :
            # Read was unsuccessful
            raise OSError();
        # std::cout << *str << " and size of string =" << str->size() << "\r\n";
        if (self.receiver is not None):
            self.receiver.OnData(data);
        
        # If code reaches here, read must of been successful
    
    def ThreadMethod(self):                    
        while(self.state == State.OPEN):        
            self.Read();                
    
    
         
        
        