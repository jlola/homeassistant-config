"""Support for Modbus Register sensors."""
import logging
import struct
from typing import Any, Optional, Union
from .IModifiedModbusHub import IModifiedModbusHub
import pydevd

from homeassistant.components.sensor import DEVICE_CLASSES_SCHEMA, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_NAME,
    CONF_OFFSET,
    CONF_SLAVE,
    CONF_STRUCTURE,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
import voluptuous as vol

from .const import (        
    CONF_COUNT,
    CONF_DATA_TYPE,
    CONF_HUB,
    CONF_HOLDINGS,
    CONF_ONEWIRE_ID,    
    CONF_REGISTERS,
    DATA_TYPE_CUSTOM,
    DATA_TYPE_FLOAT,
    DATA_TYPE_INT,
    DATA_TYPE_STRING,
    DATA_TYPE_UINT,
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
        vol.Required(CONF_HOLDINGS): [
            {
                vol.Required(CONF_NAME): cv.string,                
                vol.Required(CONF_ONEWIRE_ID): cv.string,
                vol.Required(CONF_DEVICE_CLASS): DEVICE_CLASSES_SCHEMA,
                vol.Required(CONF_HUB, default=DEFAULT_HUB): cv.string,
                vol.Required(CONF_OFFSET): number,                                
                vol.Required(CONF_SLAVE): cv.positive_int,
                vol.Required(CONF_UNIT_OF_MEASUREMENT): cv.string,
            }
        ]
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Modbus sensors."""
    sensors = []
    
    for register in config[CONF_HOLDINGS]:
        
        hub_name = register[CONF_HUB]
        hub = hass.data[MODIFIED_MODBUS_DOMAIN][hub_name]
        sensors.append(
            ModbusRegisterSensor(
                hub,
                register[CONF_NAME],
                register.get(CONF_SLAVE),
                register[CONF_OFFSET],
                register.get(CONF_UNIT_OF_MEASUREMENT),
                register[CONF_ONEWIRE_ID],                                                                                                
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
        offset,
        unit_of_measurement,
        _onewireid,                                
        device_class,
    ):
        """Initialize the modbus register sensor."""
        self._hub:IModifiedModbusHub = hub
        self._name = name
        self._slave = int(slave) if slave else None           
        self._unit_of_measurement = unit_of_measurement
        self._onewireid = _onewireid
        self._count = 1                
        self._offset = offset                        
        self._device_class = device_class
        self._value = None
        self._available = True

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
            
                result = self._hub.readHoldings(
                    self._slave, self._offset, self._count,150)
                
        except Exception as args:
            _LOGGER.error(args.args)
            self._available = False
            return

        self._value = f"{result[0]/100}"

        self._available = True   