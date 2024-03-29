"""Constants for the modified_modbus integration."""


"""Constants used in modbus integration."""

# configuration names
CONF_HOST = "host"
CONF_BAUDRATE = "baudrate"
CONF_BYTESIZE = "bytesize"
CONF_HUB = "hub"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"
CONF_HOLDING = "holding"
CONF_HOLDINGS = "holdings"
CONF_HOLDINGS_TYPE = "holdings_type"
CONF_DS18B20 = "ds18b20"
CONF_RFID = "RFID"
CONF_STRING = "string"
CONF_HEX = "hex"
CONF_NUMBER = "NUMBER"
CONF_REGISTER = "register"
CONF_REGISTER_TYPE = "register_type"
CONF_REGISTERS = "registers"
CONF_REVERSE_ORDER = "reverse_order"
CONF_SCALE = "scale"
CONF_COUNT = "count"
CONF_PRECISION = "precision"
CONF_OFFSET = "offset"
CONF_COILS = "coils"
CONF_BIT = "bit"
CONF_OWID = "OwId"

# integration names
DEFAULT_HUB = "default"
MODIFIED_MODBUS_DOMAIN = "modified_modbus"

# data types
DATA_TYPE_CUSTOM = "custom"
DATA_TYPE_FLOAT = "float"
DATA_TYPE_INT = "int"
DATA_TYPE_UINT = "uint"
DATA_TYPE_STRING = "string"

# call types
CALL_TYPE_COIL = "coil"
CALL_TYPE_DISCRETE = "discrete_input"
CALL_TYPE_HOLDING = "holding"
CALL_TYPE_REGISTER_INPUT = "input"

# the following constants are TBD.
# changing those in general causes a breaking change, because
# the contents of configuration.yaml needs to be updated,
# therefore they are left to a later date.
# but kept here, with a reference to the file using them.

# __init.py
ATTR_ADDRESS = "address"
ATTR_HUB = "hub"
ATTR_UNIT = "unit"
ATTR_SLAVE = "slave"
ATTR_VALUE = "value"
ATTR_COUNT = "count"
ATTR_TIMEOUTMS = "timeoutms"
SERVICE_WRITE_HOLDING = "write_holding"
SERVICE_READ_HOLDING = "read_holding"
SERVICE_WRITE_HOLDING = "write_holding"
SERVICE_READ_HOLDINGS = "read_holdings"
SERVICE_SCAN_UNIT = "scan_unit"

CONF_DATA_TYPE = "data_type"

# binary_sensor.py
CONF_INPUTS = "inputs"
CONF_INPUT_TYPE = "input_type"
CONF_ADDRESS = "address"
CONF_HOLDING = "holding"
CONF_HOLDING_VALUE_ON = "value_on"
CONF_HOLDING_VALUE_OFF = "value_off"

#ds18b20
CONF_ONEWIRE_ID = "ONEWIRE_ID"

# switch.py
CONF_STATE_OFF = "state_off"
CONF_STATE_ON = "state_on"
CONF_VERIFY_REGISTER = "verify_register"
CONF_VERIFY_STATE = "verify_state"