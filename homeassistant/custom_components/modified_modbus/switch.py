"""Support for Modbus switches."""
import logging
from typing import Optional

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_COMMAND_OFF,
    CONF_COMMAND_ON,
    CONF_NAME,
    CONF_SLAVE,
    STATE_ON,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.restore_state import RestoreEntity
import voluptuous as vol

from .const import (
    CALL_TYPE_COIL,
    CALL_TYPE_HOLDING,
    CONF_OFFSET,    
    CONF_HOLDINGS,
    CONF_HUB,    
    CONF_REGISTER_TYPE,    
    CONF_STATE_OFF,
    CONF_STATE_ON,
    CONF_VERIFY_REGISTER,
    CONF_VERIFY_STATE,
    DEFAULT_HUB,
    MODIFIED_MODBUS_DOMAIN,
)

from .IModifiedModbusHub import IModifiedModbusHub


_LOGGER = logging.getLogger(__name__)


HOLDINGS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COMMAND_OFF): cv.positive_int,
        vol.Required(CONF_COMMAND_ON): cv.positive_int,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_OFFSET): cv.positive_int,
        vol.Optional(CONF_HUB, default=DEFAULT_HUB): cv.string,
        vol.Optional(CONF_REGISTER_TYPE, default=CALL_TYPE_HOLDING): vol.In(
            [CALL_TYPE_HOLDING]
        ),
        vol.Optional(CONF_SLAVE): cv.positive_int,
        vol.Optional(CONF_STATE_OFF): cv.positive_int,
        vol.Optional(CONF_STATE_ON): cv.positive_int,
        vol.Optional(CONF_VERIFY_REGISTER): cv.positive_int,
        vol.Optional(CONF_VERIFY_STATE, default=True): cv.boolean,
    }
)

COILS_SCHEMA = vol.Schema(
    {
        vol.Required(CALL_TYPE_COIL): cv.positive_int,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SLAVE): cv.positive_int,
        vol.Optional(CONF_HUB, default=DEFAULT_HUB): cv.string,
    }
)

PLATFORM_SCHEMA = vol.All(
    cv.has_at_least_one_key(CONF_HOLDINGS),
    PLATFORM_SCHEMA.extend(
        {
            vol.Optional(CONF_HOLDINGS): [HOLDINGS_SCHEMA],
        }
    ),
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Read configuration and create Modbus devices."""
    switches = []    
    if CONF_HOLDINGS in config:
        for register in config[CONF_HOLDINGS]:
            hub_name = register[CONF_HUB]
            hub = hass.data[MODIFIED_MODBUS_DOMAIN][hub_name]

            switches.append(
                ModbusRegisterSwitch(
                    hub,
                    register[CONF_NAME],
                    register.get(CONF_SLAVE),
                    register[CONF_OFFSET],
                    register[CONF_COMMAND_ON],
                    register[CONF_COMMAND_OFF],
                    register[CONF_VERIFY_STATE],
                    register.get(CONF_VERIFY_REGISTER),
                    register[CONF_REGISTER_TYPE],
                    register.get(CONF_STATE_ON),
                    register.get(CONF_STATE_OFF),
                )
            )

    add_entities(switches)


class ModbusEntity(ToggleEntity, RestoreEntity):
    """Representation of a Modbus coil switch."""

    def __init__(self, hub, name, slave, coil):
        """Initialize the coil switch."""
        self._hub = hub
        self._name = name
        self._slave = int(slave) if slave else None
        self._coil = int(coil)
        self._is_on = None
        self._available = True

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        state = await self.async_get_last_state()
        if not state:
            return
        self._is_on = state.state == STATE_ON

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._is_on

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    def turn_on(self, **kwargs):
        """Set switch on."""
        self._write_coil(self._coil, True)

    def turn_off(self, **kwargs):
        """Set switch off."""
        self._write_coil(self._coil, False)
    

class ModbusRegisterSwitch(ModbusEntity):
    """Representation of a Modbus register switch."""

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        hub:IModifiedModbusHub,
        name,
        slave,
        register,
        command_on,
        command_off,
        verify_state,
        verify_register,
        register_type,
        state_on,
        state_off,
    ):
        """Initialize the register switch."""
        self._hub:IModifiedModbusHub = hub
        self._name = name
        self._slave = slave
        self._register = register
        self._command_on = command_on
        self._command_off = command_off
        self._verify_state = verify_state
        self._verify_register = verify_register if verify_register else self._register
        self._register_type = register_type
        self._available = True

        if state_on is not None:
            self._state_on = state_on
        else:
            self._state_on = self._command_on

        if state_off is not None:
            self._state_off = state_off
        else:
            self._state_off = self._command_off

        self._is_on = None

    def turn_on(self, **kwargs):
        """Set switch on."""

        # Only holding register is writable        
        self._write_register(self._command_on)
        if not self._verify_state:
            self._is_on = True

    def turn_off(self, **kwargs):
        """Set switch off."""

        # Only holding register is writable        
        self._write_register(self._command_off)
        if not self._verify_state:
            self._is_on = False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Update the state of the switch."""
        if not self._verify_state:
            return

        value = self._read_register()
        if value == self._state_on:
            self._is_on = True
        elif value == self._state_off:
            self._is_on = False
        elif value is not None:
            _LOGGER.error(
                "Unexpected response from hub %s, slave %s register %s, got 0x%2x",
                self._hub.ConfigName,
                self._slave,
                self._register,
                value,
            )

    def _read_register(self) -> Optional[int]:
        try:            
            result = self._hub.readHolding(
                self._slave, self._verify_register
            )
        except Exception as args:
            _LOGGER.exception(args.args)
            self._available = False
            return

        
        self._available = True

        return int(result)
    
    def _write_register(self, value):
        """Write holding register using the Modbus hub slave."""
        try:
            self._hub.writeHolding(self._slave, self._register, value)
        except Exception as args:
            _LOGGER.exception(args.args)
            self._available = False
            return

        self._available = True
