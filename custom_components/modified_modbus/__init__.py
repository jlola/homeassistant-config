"""Support for Modbus."""
import importlib
import logging
import threading
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
        unit = int(float(service.data[ATTR_UNIT]))
        address = int(float(service.data[ATTR_ADDRESS]))    
        value = int(float(service.data[ATTR_VALUE]))    
        client_name = service.data[ATTR_HUB]  
        
        hub_collect[client_name].writeHolding(unit, address,value)

    def read_holding(service):
        """Read holding"""
        unit = int(float(service.data[ATTR_UNIT]))
        address = int(float(service.data[ATTR_ADDRESS]))    
        client_name = service.data[ATTR_HUB]    
        
        result = hub_collect[client_name].readHolding(unit, address)
        hass.states.set("modified_modbus.read_holding", result)
    
    def scan_unit(service):                
        unit = int(float(service.data[ATTR_UNIT]))
        client_name = service.data[ATTR_HUB]                    
        result = hub_collect[client_name].scanUnit(unit)
    
    def read_holdings(service):
        """Read holdings"""
        unit = int(float(service.data[ATTR_UNIT]))
        address = int(float(service.data[ATTR_ADDRESS]))    
        client_name = service.data[ATTR_HUB]    
        count = int(float(service.data[ATTR_COUNT]))
        timeout = int(float(service.data[ATTR_TIMEOUTMS]))

        result = hub_collect[client_name].readHoldings(unit, address, count, timeout) 

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
            self._client.AddConsumer(self)
        else:
            assert False

        # Connect device
        self.connect()
        
    def scanUnit(self,unit:int):
        scanner = UnitScanner(self)
        scanner.Scan(unit)

    def AddConsumer(self,consumer:IDeviceEventConsumer):
        self._client.AddConsumer(consumer)

    def FireEvent(self,adr:int):        
        self.resetChangeFlag(adr) 

    def readHolding(self,unit:int,adr:int):
        with self._lock:
            bufferbytes = self._client.getHoldings(unit,adr,1)    
            return bufferbytes[0]        
    
    def readHoldings(self,unit:int,adr:int,count:int, timeout:int):
        with self._lock:
            bufferbytes = self._client.getHoldings(unit,adr,count,timeoutMs=timeout)        
        return bufferbytes        
    
    def writeHolding(self,adr:int,offset:int,value:int):
        with self._lock:
            self._client.setHolding(adr,offset,value)
    
    def resetChangeFlag(self,adr:int):
        print(f"received alarm from unit: {adr}")
        with self._lock:
            self._client.setHolding(adr,CHANGE_FLAG,1)

    def connect(self):
        """Connect client."""
        with self._lock:
            self._client.Open()
    
    def disconnect(self):
        with self._lock:
            self._client.Close()

