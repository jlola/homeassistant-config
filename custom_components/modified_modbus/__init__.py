"""Support for Modbus."""
import importlib
import logging
import threading
from datetime import datetime

from interface import implements
from .IModifiedModbusHub import IModifiedModbusHub

from .ModifiedModbus.IDeviceEventConsumer import IDeviceEventConsumer
from .ModifiedModbus import ModifiedModbus
from homeassistant.const import (
    ATTR_STATE,
    CONF_DELAY,
    CONF_HOST,
    CONF_METHOD,
    CONF_NAME,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_TYPE,
    EVENT_HOMEASSISTANT_STOP,
)

import homeassistant.helpers.config_validation as cv

import voluptuous as vol

from .const import (
    ATTR_ADDRESS,
    ATTR_HUB,
    ATTR_UNIT,
    ATTR_VALUE,
    ATTR_COUNT,
    ATTR_TIMEOUTMS,
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_PARITY,
    CONF_STOPBITS,
    DEFAULT_HUB,
    MODIFIED_MODBUS_DOMAIN as DOMAIN,
    SERVICE_WRITE_HOLDING,
    SERVICE_READ_HOLDING,
    SERVICE_READ_HOLDINGS,
    SERVICE_SCAN_UNIT
)
from _datetime import date

DEVICEBASE = 0
DEVADDR_OFFSET = DEVICEBASE+0
COUNT_OF_TYPES_OFFSET = DEVICEBASE+1
TYPE_DEFS_OFFSET = DEVICEBASE+2
RESET_REG_OFFSET = DEVICEBASE+3
LAST_INDEX = DEVICEBASE+4
CHANGE_FLAG = DEVICEBASE+5

from .unit_scanner import UnitScanner

_LOGGER = logging.getLogger(__name__)


BASE_SCHEMA = vol.Schema({vol.Optional(CONF_NAME, default=DEFAULT_HUB): cv.string})

SERIAL_SCHEMA = BASE_SCHEMA.extend(
    {
        vol.Required(CONF_BAUDRATE): cv.positive_int,
        vol.Required(CONF_BYTESIZE): vol.Any(5, 6, 7, 8),
        vol.Required(CONF_METHOD): vol.Any("rtu", "ascii"),
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_PARITY): vol.Any("E", "O", "N"),
        vol.Required(CONF_STOPBITS): vol.Any(1, 2),
        vol.Required(CONF_TYPE): "serial",
        vol.Optional(CONF_TIMEOUT, default=3): cv.socket_timeout,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [vol.Any(SERIAL_SCHEMA)])},
    extra=vol.ALLOW_EXTRA,
)

SERVICE_WRITE_HOLDING_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_HUB, default=DEFAULT_HUB): cv.string,
        vol.Required(ATTR_UNIT): cv.positive_int,
        vol.Required(ATTR_ADDRESS): cv.positive_int,
        vol.Required(ATTR_VALUE): vol.Any(
            cv.positive_int, vol.All(cv.ensure_list, [cv.positive_int])
        ),
    }
)

SERVICE_READ_HOLDING_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_HUB, default=DEFAULT_HUB): cv.string,
        vol.Required(ATTR_UNIT): cv.positive_int,
        vol.Required(ATTR_ADDRESS): cv.positive_int        
    }
)

SERVICE_WRITE_HOLDING_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_HUB, default=DEFAULT_HUB): cv.string,
        vol.Required(ATTR_UNIT): cv.positive_int,
        vol.Required(ATTR_ADDRESS): cv.positive_int,
        vol.Required(ATTR_VALUE): cv.positive_int
    }
)

SERVICE_READ_HOLDINGS_SCHEMA = vol.Schema(    
    {
        vol.Optional(ATTR_HUB, default=DEFAULT_HUB): cv.string,
        vol.Required(ATTR_UNIT): cv.positive_int,
        vol.Required(ATTR_ADDRESS): cv.positive_int,
        vol.Required(ATTR_COUNT): cv.positive_int,
        vol.Required(ATTR_TIMEOUTMS): cv.positive_int
    }
)

SERVICE_SCAN_SCHEMA = vol.Schema(    
    {
        vol.Optional(ATTR_HUB, default=DEFAULT_HUB): cv.string,
        vol.Required(ATTR_UNIT): cv.positive_int,            
        vol.Optional(ATTR_TIMEOUTMS,150): cv.positive_int
    }
)

def setup(hass, config):    
    """Set up Modified modbus component."""
    hass.data[DOMAIN] = hub_collect = {}

    for client_config in config[DOMAIN]:
        hub_collect[client_config[CONF_NAME]] = ModifiedModbusHub(client_config)

    def stop_modbus(event):
        """Stop Modbus service."""
        #for client in hub_collect.values():
        #    client.close()
        # Return boolean to indicate that initialization was successful.

    def write_holding(service):
        """Write holding"""
        slave = int(float(service.data[ATTR_UNIT]))
        offset = int(float(service.data[ATTR_ADDRESS]))    
        value = int(float(service.data[ATTR_VALUE]))    
        client_name = service.data[ATTR_HUB]  
        
        hub_collect[client_name].writeHolding(slave, offset,value)

    def read_holding(service):
        """Read holding"""
        slave = int(float(service.data[ATTR_UNIT]))
        offset = int(float(service.data[ATTR_ADDRESS]))    
        client_name = service.data[ATTR_HUB]    
        
        result = hub_collect[client_name].readHolding(slave, offset)
        hass.states.set("modified_modbus.read_holding", result)
    
    def scan_unit(service):                
        slave = int(float(service.data[ATTR_UNIT]))
        client_name = service.data[ATTR_HUB]                    
        result = hub_collect[client_name].scanUnit(slave)
    
    def read_holdings(service):
        """Read holdings"""
        slave = int(float(service.data[ATTR_UNIT]))
        offset = int(float(service.data[ATTR_ADDRESS]))    
        client_name = service.data[ATTR_HUB]    
        count = int(float(service.data[ATTR_COUNT]))
        timeout = int(float(service.data[ATTR_TIMEOUTMS]))

        result = hub_collect[client_name].readHoldings(slave, offset, count, timeout) 

    # do not wait for EVENT_HOMEASSISTANT_START, activate pymodbus now
    for client in hub_collect.values():
        client.setup()

    # Register services for modbus
    hass.services.register(
        DOMAIN,
        SERVICE_READ_HOLDING,
        read_holding,
        schema=SERVICE_READ_HOLDING_SCHEMA,
    )

    hass.services.register(
        DOMAIN,
        SERVICE_WRITE_HOLDING,
        write_holding,
        schema=SERVICE_WRITE_HOLDING_SCHEMA,
    )

    hass.services.register(
        DOMAIN,
        SERVICE_READ_HOLDINGS,
        read_holdings,
        schema=SERVICE_READ_HOLDINGS_SCHEMA,
    )
    
    hass.services.register(
        DOMAIN,
        SERVICE_SCAN_UNIT,
        scan_unit,
        schema=SERVICE_SCAN_SCHEMA,
    )

    return True

class SlaveCache():        
    def __init__(self,slave):
        self.refreshTime:datetime = None
        self.holdings = []
        self.slave = slave
        self.cacheExpiredInSeconds = 5
    
    def NeedRefresh(self) -> bool:        
        now = datetime.now()
        if (self.refreshTime==None):
            return True
        delta = (now - self.refreshTime).total_seconds()
        if (delta > self.cacheExpiredInSeconds):
            return True
        
        return False    
    
    def GetHoldings(self,offset,count):
        if (offset+count > len(self.holdings)):
            raise Exception(f"requested: offset: {offset}, count: {count} out of range")
            
        return self.holdings[offset:offset+count]
    
    def GetCacheData(self):
        return self.holdings
    
    def SetUpdatedData(self,data):
        self.holdings = data
        self.refreshTime = datetime.now()
        
class ModbusCache():
    DEVICEBASE =                    0
    LAST_INDEX =                    DEVICEBASE+4
    def __init__(self,serial:ModifiedModbus):
        self._serial = serial
        self.dict = {}
        
    def getSlaveCache(self,slave)->SlaveCache:
        if (not slave in self.dict):
            self.dict[slave] = SlaveCache(slave)
        
        return self.dict[slave]
    
    def ForceRefresh(self,slave):
        slaveCache = self.getSlaveCache(slave)
        slaveCache.refreshTime = None
    
    def getHoldings(self,slave,offset,count):
        cache = self.getSlaveCache(slave)
        if (cache.NeedRefresh()):            
            lastIndex = self._serial.getHoldings(slave, LAST_INDEX, 1)            
            holdings = self._serial.getHoldings(slave, 0, lastIndex[0], 150)
            cache.SetUpdatedData(holdings)
        
        cachedHoldings = cache.GetHoldings(offset,count)
        return cachedHoldings
        
    
        
    
    


class ModifiedModbusHub(IDeviceEventConsumer,IModifiedModbusHub):
    """wrapper class for ModifiedModbus."""
    def __init__(self, client_config):
        """Initialize the Modbus hub."""
        
        # generic configuration
        self._client = None
        self._lock = threading.Lock()
        self._config_name = client_config[CONF_NAME]
        self._config_type = client_config[CONF_TYPE]
        self._config_port = client_config[CONF_PORT]
        self._config_timeout = client_config[CONF_TIMEOUT]
        self._config_delay = 0
        self._consumers = []        
        self._modbusCacheTimeout:datetime = datetime.now()

        if self._config_type == "serial":
            # serial configuration
            self._config_method = client_config[CONF_METHOD]
            self._config_baudrate = client_config[CONF_BAUDRATE]
            self._config_stopbits = client_config[CONF_STOPBITS]
            self._config_bytesize = client_config[CONF_BYTESIZE]
            self._config_parity = client_config[CONF_PARITY]
        else:
            # network configuration
            self._config_host = client_config[CONF_HOST]
            self._config_delay = client_config[CONF_DELAY]
            if self._config_delay > 0:
                _LOGGER.warning(
                    "Parameter delay is accepted but not used in this version"
                )

    @property
    def ConfigName(self):
        return self._config_name    
        
    def setup(self):
        """Set up pymodbus client."""
        if self._config_type == "serial":            
            self._client = ModifiedModbus(self._config_port,self._config_baudrate)
            self._modbusCache = ModbusCache(self._client)
            self._client.AddConsumer(self)
        else:
            assert False

        # Connect device
        self.connect()
        
    def scanUnit(self,unit:int):
        scanner = UnitScanner(self)
        scanner.Scan(unit)

    def AddConsumer(self,consumer:IDeviceEventConsumer):
        #self._client.AddConsumer(consumer)
        self._consumers.append(consumer)

    def FireEvent(self,slave:int):                
        self.resetChangeFlag(slave)
        self._modbusCache.ForceRefresh(slave) 
        for c in self._consumers:            
            c.FireEvent(slave)

    def readHolding(self,slave:int,offset:int):
        with self._lock:
#             _LOGGER.debug(f"readHolding slave:{slave},offset:{offset}")
            bufferbytes = self._modbusCache.getHoldings(slave, offset, 1)  
#             _LOGGER.debug(f"readHolding slave finished:{slave},offset:{offset}")  
            return bufferbytes[0]
            
    
    def readHoldings(self,slave:int,offset:int,count:int, timeout:int):
        with self._lock:
#             _LOGGER.debug(f"readHoldings slave:{slave},offset:{offset},count:{count}")
            bufferbytes = self._modbusCache.getHoldings(slave, offset, count)      
#             _LOGGER.debug(f"readHoldings finished slave:{slave},offset:{offset},count:{count}")  
            return bufferbytes        
    
    def writeHolding(self,slave:int,offset:int,value:int):
        with self._lock:
#             _LOGGER.debug(f"writeHolding slave:{slave},offset:{offset}")
            self._client.setHolding(slave,offset,value)
#             _LOGGER.debug(f"writeHolding finished slave:{slave},offset:{offset}")
    
    def resetChangeFlag(self,slave:int):
        with self._lock:
#             _LOGGER.debug(f"writeHolding reset change flag: slave:{slave},offset:{CHANGE_FLAG}")
            self._client.setHolding(slave,CHANGE_FLAG,1)
#             _LOGGER.debug(f"writeHolding reset change finished flag: slave:{slave},offset:{CHANGE_FLAG}")

    def connect(self):
        """Connect client."""
        with self._lock:
            self._client.Open()
    
    def disconnect(self):
        with self._lock:
            self._client.Close()

