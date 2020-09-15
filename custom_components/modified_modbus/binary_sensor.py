"""Support for Modbus Coil and Discrete Input sensors."""
from abc import ABC
import logging
from typing import Optional

from .ModifiedModbus import IDeviceEventConsumer
from homeassistant.components.binary_sensor import (
    DEVICE_CLASSES_SCHEMA,
    PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.const import CONF_DEVICE_CLASS, CONF_NAME, CONF_SLAVE
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    CALL_TYPE_COIL,
    CALL_TYPE_DISCRETE,
    CALL_TYPE_HOLDING,
    CONF_ADDRESS,
    CONF_COILS,
    CONF_HUB,
    CONF_INPUT_TYPE,
    CONF_INPUTS,
    DEFAULT_HUB,
    MODIFIED_MODBUS_DOMAIN,
    CONF_HOLDING_VALUE_ON,
    CONF_HOLDING_VALUE_OFF,
    CONF_HOLDINGS
)


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.All( 
    PLATFORM_SCHEMA.extend(
        {     
            vol.Required(CONF_HOLDINGS): [
                vol.All(                    
                    vol.Schema(
                        {
                            vol.Required(CONF_ADDRESS): cv.positive_int,
                            vol.Required(CONF_NAME): cv.string,
                            vol.Optional(CONF_DEVICE_CLASS): DEVICE_CLASSES_SCHEMA,
                            vol.Optional(CONF_HUB, default=DEFAULT_HUB): cv.string,
                            vol.Required(CONF_SLAVE): cv.positive_int,
                            vol.Required(CONF_HOLDING_VALUE_ON):cv.positive_int,
                            vol.Required(CONF_HOLDING_VALUE_OFF):cv.positive_int                    
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
                entry[CONF_ADDRESS],
                entry.get(CONF_DEVICE_CLASS),                
                entry[CONF_HOLDING_VALUE_ON],
                entry[CONF_HOLDING_VALUE_OFF]
            )
        )

    add_entities(sensors)


class ModifiedModbusBinarySensor(BinarySensorEntity,IDeviceEventConsumer):
    """Modbus binary sensor."""

    def __init__(self, hub, name, slave, address, device_class, value_on,value_off):
        """Initialize the Modbus binary sensor."""
        self._hub = hub
        self._name = name
        self._slave = int(slave) if slave else None
        self._address = int(address)
        self._device_class = device_class        
        self._value = None
        self._available = True
        self._value_on = value_on
        self._value_off = value_off
        self._hub.AddConsumer(self)
    
    def FireEvent(self,adr:int):
        self.async_update_ha_state(force_refresh = True)

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
        try:
            result = self._hub.readHolding(self._slave,self._address)        
        except Exception:
            self._available = False
            return    

        self._available = True

        if (result == self._value_on):
            self._value = True
        elif (result == self._value_off):
            self._value = False
        else:
            self._available = False

        
