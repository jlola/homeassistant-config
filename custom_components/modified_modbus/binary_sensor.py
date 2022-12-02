"""Support for Modbus Coil and Discrete Input sensors."""
#from abc import ABC
import logging
from typing import Optional
#import pydevd
from .ModifiedModbus import IDeviceEventConsumer
from .ModifiedModbus.Helper import Helper
from homeassistant.components.binary_sensor import (
    DEVICE_CLASSES_SCHEMA,
    PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.const import (
    CONF_DEVICE_CLASS, 
    CONF_NAME, 
    CONF_SLAVE
)
from homeassistant.helpers import config_validation as cv
from .IModifiedModbusHub import IModifiedModbusHub
import voluptuous as vol

from .const import (
    CONF_HUB,
    DEFAULT_HUB,
    MODIFIED_MODBUS_DOMAIN,
    CONF_HOLDING_VALUE_ON,
    CONF_HOLDING_VALUE_OFF,
    CONF_HOLDINGS,
    CONF_OFFSET,
    CONF_BIT
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.All( 
    PLATFORM_SCHEMA.extend(
        {     
            vol.Required(CONF_HOLDINGS): [
                vol.All(                    
                    vol.Schema(
                        {
                            vol.Required(CONF_OFFSET): cv.positive_int,
                            vol.Required(CONF_NAME): cv.string,
                            vol.Optional(CONF_DEVICE_CLASS): DEVICE_CLASSES_SCHEMA,
                            vol.Optional(CONF_HUB, default=DEFAULT_HUB): cv.string,
                            vol.Required(CONF_SLAVE): cv.positive_int,
                            vol.Optional(CONF_HOLDING_VALUE_ON):cv.positive_int,
                            vol.Optional(CONF_HOLDING_VALUE_OFF):cv.positive_int,
                            vol.Optional(CONF_BIT,default=-1):cv.positive_int                   
                        }
                    ),
                )
            ]    
        }
    ),
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Modbus binary sensors."""
    sensors = []
    for entry in config[CONF_HOLDINGS]:
        hub = hass.data[MODIFIED_MODBUS_DOMAIN][entry[CONF_HUB]]
        sensors.append(
            ModifiedModbusBinarySensor(
                hub,
                entry[CONF_NAME],
                entry.get(CONF_SLAVE),
                entry[CONF_OFFSET],
                entry.get(CONF_DEVICE_CLASS),                
                entry[CONF_HOLDING_VALUE_ON],
                entry[CONF_HOLDING_VALUE_OFF],
                entry[CONF_BIT]
            )
        )

    add_entities(sensors)


class ModifiedModbusBinarySensor(BinarySensorEntity,IDeviceEventConsumer):
    """Modbus binary sensor."""

    def __init__(self, hub:IModifiedModbusHub, name, slave, offset, device_class, value_on,value_off,bit):
        """Initialize the Modbus binary sensor."""
        self._hub = hub
        self._name = name
        self._slave = int(slave) if slave else None
        self._offset = int(offset)
        self._device_class = device_class        
        self._value = None
        self._available = True
        self._value_on = value_on
        self._value_off = value_off
        self._hub.AddConsumer(self)
        self._bit = bit
            
    def FireEvent(self,slave:int):
        if (slave == self._slave):
            _LOGGER.info(f"binary_input| force refresh slave: {self._slave}")
            self.schedule_update_ha_state(force_refresh=True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    def update(self):        
        """Update the state of the sensor."""
        #pydevd.settrace("192.168.89.25", port=5678)
        try:
            result = self._hub.readHolding(self._slave, self._offset)        
        except Exception as arg:
            _LOGGER.error(arg.args)
            print(f"slave: {self._slave} available false exception")
            self._available = False
            return    

        self._available = True
        print("{0:04X} ".format(result))
#         if (result == self._value_on):
#             self._value = True
#         elif (result == self._value_off):
#             self._value = False
#         else:
#             print(f"slave: {self._slave} available false, received {result} expected on {self._value_on} expected off {self._value_off}")
#             self._available = False
        try:
            self._value = self.GetBoolValue(result)
        except Exception as arg:
            _LOGGER.error(arg.args)
            print(f"slave: {self._slave} available false exception")
            self._available = False
        
    
            
    def GetBoolValue(self,value):
        if (self._bit!=None or self._bit < 0):
            return Helper.BitValue(value,self._bit)
        else:
            if (value == self._valueOn):
                return True
            elif (value == self._valueOff):
                return False
            else:
                raise Exception("Incorrect value")            

        
