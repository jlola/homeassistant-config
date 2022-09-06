from enum import Enum
import threading;
from .ISerialReceiver import ISerialReceiver
import socket
import time
import logging

class State(Enum):
    OPEN=0,
    CLOSE=1

_LOGGER = logging.getLogger(__name__)

class SocketClient(object):
    '''
    classdocs
    '''
    def __init__(self, address:str, port:str):
        '''
        Constructor        
        '''
        self.port = int(port)
        self.address = address
        self.state = State.CLOSE    
        self.timeoutMs = 0.05
        self.minBytes = 7
        self.socket = None
        self.connected = False
        self.receiver = None
        self.fulladdress = f"{self.address}:{self.port}"


    def is_socket_closed(self,sock: socket.socket) -> bool:
        if (sock is None):
            return True
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            timeout = sock.gettimeout()
            sock.settimeout(0)
            sock.setblocking(False)
            data = sock.recv(16, socket.MSG_PEEK)
            if len(data) == 0:
                return True
        except BlockingIOError:
            return False  # socket is open and reading from it would block
        except ConnectionResetError:
            return True  # socket was closed for some other reason
        except Exception as e:
            return False
        finally:
            sock.setblocking(True)
            sock.settimeout(timeout)
        return False

    def OnData(self, data:list):
        pass

    def Open(self):
        if (self.state == State.OPEN) :
            return
        
        self.state = State.OPEN
        self.thread = threading.Thread(target=self.ThreadMethod)
        self.thread.start()        

    def Close(self):
        if (self.state == State.CLOSE) :
            return
        self.state = State.CLOSE
        self.socket.close()

    def SetReceiver(self, receiver: ISerialReceiver):
        self.receiver = receiver

    def Write(self,data:bytes):
        if(self.state != State.OPEN):
            raise NameError(" called but state != OPEN. Please call Open() first.")
        
        if (self.connected == False):
            self.connect()

        try:
            writeResult = self.socket.send(data)
        except Exception as e:
            raise NameError(f"Socket is not connected to {self.fulladdress}: {e}")
            writeResult = -1
        # Check status        
        return writeResult

    def connect(self):    
        if (self.connected):
            return
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.address, self.port))
            self.connected = True
            print(f"connected to {self.fulladdress}")
            _LOGGER.info(f"connected to {self.fulladdress}")
        except Exception as e:
            self.connected = False
            print(f"connect failed {e}")
            time.sleep(1)

        #and nick, pass, and join stuffs        
    def GetName(self):
        return "SocketClient"
        
    def Read(self) :
        if(self.state != State.OPEN):
            raise NameError(" called but state != OPEN. Please call Open() first.")
        if (not self.connected):
            self.connect()
        
        # Read from file
        # We provide the underlying raw array from the readBuffer_ vector to this C api.
        # This will work because we do not delete/resize the vector while this method
        # is called
        try:
            self.socket.settimeout(5.0)
            if self.socket is not None:      
                data = self.socket.recv(1024);
            else:
                data = bytes()
        except Exception as e:
            data = bytes()
            self.connected = False
            _LOGGER.info(f"Socket error 5s {e}")
                
        # std::cout << *str << " and size of string =" << str->size() << "\r\n";
        if (self.socket is not None and len(data)>0 and self.receiver is not None):
            self.receiver.OnData(data);

    def ThreadMethod(self):                    
        while(self.state == State.OPEN):        
            self.Read();   