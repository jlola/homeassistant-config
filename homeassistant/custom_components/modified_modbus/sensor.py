"""Support for Modbus Register sensors."""
import logging
from typing import Any, Optional, Union
from .IModifiedModbusHub import IModifiedModbusHub
#import pydevd
from .unit_scanner import UnitScanner 

from homeassistant.components.sensor import DEVICE_CLASSES_SCHEMA, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_NAME,    
    CONF_SLAVE,    
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
import voluptuous as vol

from .const import (            
    CONF_OWID,
    CONF_HUB,    
    CONF_DS18B20,        
    DEFAULT_HUB,
    MODIFIED_MODBUS_DOMAIN,
)


_LOGGER = logging.getLogger(__name__)


def number(value: Any) -> Union[int, float]:
    """Coerce a value to number without losing precision."""
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        try:
            value = int(value)
            return value
        except (TypeError, ValueError):
            pass

    try:
        value = float(value)
        return value
    except (TypeError, ValueError) as err:
        raise vol.Invalid(f"invalid number {value}") from err


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DS18B20): [
            {
                vol.Required(CONF_NAME): cv.string,                
                vol.Required(CONF_OWID): cv.string,
                vol.Required(CONF_DEVICE_CLASS): DEVICE_CLASSES_SCHEMA,
                vol.Required(CONF_HUB, default=DEFAULT_HUB): cv.string,
                vol.Required(CONF_OWID): cv.string,                                
                vol.Required(CONF_SLAVE): cv.positive_int,
                vol.Required(CONF_UNIT_OF_MEASUREMENT): cv.string,
            }
        ]
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Modbus sensors."""
    sensors = []
    
    for register in config[CONF_DS18B20]:
        
        hub_name = register[CONF_HUB]
        hub = hass.data[MODIFIED_MODBUS_DOMAIN][hub_name]
        sensors.append(
            ModbusRegisterSensor(
                hub,
                register[CONF_NAME],
                register.get(CONF_SLAVE),
                register[CONF_OWID],
                register.get(CONF_UNIT_OF_MEASUREMENT),                                                                                                            
                register.get(CONF_DEVICE_CLASS),
            )
        )

    if not sensors:
        return False
    add_entities(sensors)


class ModbusRegisterSensor(RestoreEntity):
    """Modbus register sensor."""

    def __init__(
        self,
        hub:IModifiedModbusHub,
        name,
        slave,                
        owid,
        unit_of_measurement,        
        device_class,
    ):
        """Initialize the modbus register sensor."""
        self._hub:IModifiedModbusHub = hub
        self._name = name
        self._slave = int(slave) if slave else None           
        self._unit_of_measurement = unit_of_measurement                        
        self._owid = owid                        
        self._device_class = device_class
        self._value = None
        self._available = True
        self.scanner = UnitScanner(self._hub,self._slave)

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        state = await self.async_get_last_state()
        if not state:
            return
        self._value = state.state

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

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
            self._value =  self.scanner.GetDS18B20Value(self._owid)      
        except Exception as args:
            _LOGGER.error(args.args)
            self._available = False
            return
        
        self._available = True   