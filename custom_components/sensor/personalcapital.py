"""
Support for Personal Capital sensors.

For more details about this platform, please refer to the documentation at
https://github.com/custom-components/sensor.personalcapital
"""

import logging
import voluptuous as vol
import json
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)

__version__ = '0.0.1'

REQUIREMENTS = ['personalcapital==1.0.1']

CONF_EMAIL = 'email'
CONF_PASSWORD = 'password'
CONF_UNIT_OF_MEASUREMENT = 'unit_of_measurement'

DATA_PERSONAL_CAPITAL = 'personalcapital_cache'
DATA = 'personalcapital_data'

SCAN_INTERVAL = timedelta(seconds=500)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT, default='USD'): cv.string,
})

_LOGGER = logging.getLogger(__name__)

# def request_configuration(hass, config, url, add_devices_callback):
#     """Request configuration steps from the user."""
#     configurator = hass.components.configurator
#     if 'personalcapital' in _CONFIGURING:
#         configurator.notify_errors(
#             _CONFIGURING['personalcapital'], "Failed to register, please try again.")

#         return
#     from websocket import create_connection
#     websocket = create_connection((url), timeout=1)
#     websocket.send(json.dumps({'namespace': 'connect',
#                                'method': 'connect',
#                                'arguments': ['Home Assistant']}))

#     def personalcapital_configuration_callback(callback_data):
#         """Handle configuration changes."""
#         while True:
#             from websocket import _exceptions
#             try:
#                 msg = json.loads(websocket.recv())
#             except _exceptions.WebSocketConnectionClosedException:
#                 continue
#             if msg['channel'] != 'connect':
#                 continue
#             if msg['payload'] != "CODE_REQUIRED":
#                 continue
#             pin = callback_data.get('pin')
#             websocket.send(json.dumps({'namespace': 'connect',
#                                        'method': 'connect',
#                                        'arguments': ['Home Assistant', pin]}))
#             tmpmsg = json.loads(websocket.recv())
#             if tmpmsg['channel'] == 'time':
#                 _LOGGER.error("Error setting up Personal Captial. Please request another PIN")
#                 break
#             code = tmpmsg['payload']
#             if code == 'CODE_REQUIRED':
#                 continue
#             setup_personalcaptial(hass, config, code,
#                         add_devices_callback)
#             save_json(hass.config.path(GPMDP_CONFIG_FILE), {"CODE": code})
#             websocket.send(json.dumps({'namespace': 'connect',
#                                        'method': 'connect',
#                                        'arguments': ['Home Assistant', code]}))
#             websocket.close()
#             break

#     _CONFIGURING['personalcapital'] = configurator.request_config(
#         DEFAULT_NAME, gpmdp_configuration_callback,
#         description=(
#             'Enter the pin texted to you by PersonalCapital.'),
#         submit_caption="Submit",
#         fields=[{'id': 'pin', 'name': 'Pin Code', 'type': 'number'}]
#     )

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Personal Capital sensors."""
    from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
    pc = PersonalCapital()
    email = config.get(CONF_EMAIL)
    password = config.get(CONF_PASSWORD)
    unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)

    # TODO Restore session if available
    cookies = {}
    data_file = '{"AWSELB": "57AD13530489012C132022E50DB8A16FA96C8D7A9E004B49630961B98E55B9C8A77D44AD58DA2FF58EC64BB381F70B2BC38AF3663F23DA4E11897F22C8B77CFC44183AE0F1B491E11587B445F893AD060D40FB0F6C", "JSESSIONID": "C248C961AD7B0EC2657A7985ED5EFB18", "PMData": "34336535366461392d303462642d343764342d383939342d323738623939653938393838", "REMEMBER_ME_COOKIE": "563241454a3468594d6a72767a65774e44426b614b51354848773d3d", "__cfduid": "df8d2f8e00e72bf52e494d8d04b9ecf281534825242"}'
    try:
        cookies = json.loads(data_file)
    except ValueError as err:
        _LOGGER.error(err)

    pc.set_session(cookies)

    try:
        pc.login(email, password)
        _LOGGER.warn('PC session authenticated')
    except RequireTwoFactorException:
        _LOGGER.warn('PC session not authenticated')
        # pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, '6935')
        pc.authenticate_password(password)

    _LOGGER.warn(pc.get_session())

    add_devices([PersonalCapitalNetWorthSensor(hass, pc, unit_of_measurement)])

class PersonalCapitalNetWorthSensor(Entity):
    """Representation of a personalcapital.com net worth sensor."""

    def __init__(self, hass, pc, unit_of_measurement):
        """Initialize the sensor."""
        self._pc = pc
        self.hass = hass
        self._unit_of_measurement = unit_of_measurement
        self._state = 0
        self.hass.data[DATA] = {}
        self.update()

    def update(self):
        """Get the latest state of the sensor."""
        accounts_response = self._pc.fetch('/newaccount/getAccounts')
        _LOGGER.warn('/newaccount/getAccounts')
        _LOGGER.warn(accounts_response.json())
        accounts = accounts_response.json()['spData']

        self._state = accounts.networth


        # self._assets = self._personal_capital_data.assets
        # self._liabilities = self._personal_capital_data.liabilities
        # self._investments = self._personal_capital_data.investmentAccountsTotal
        # self._mortgages = self._personal_capital_data.mortgageAccountsTotal
        # self._cash = self._personal_capital_data.cashAccountsTotal
        # self._otherAssets =self._personal_capital_data.otherAssetAccountsTotal
        # self._otherLiabilities = self._personal_capital_data.otherLiabilitiesAccountsTotal
        # self._creditCards = self._personal_capital_data.creditCardAccountsTotal
        # self._loans = self._personal_capital_data.loanAccountsTotal

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Personal Capital Networth'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measure this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:coin'

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self.hass.data[DATA]

# class AccountSensor(Entity):
#     """Representation of a personalcapital.com sensor."""

#     def __init__(self, personal_capital_data, name, currency):
#         """Initialize the sensor."""
#         self._personal_capital_data = personal_capital_data
#         self._name = "Personal Capital {}".format(name)
#         self._state = None
#         self._acct_type = None
#         self._category = None
#         self._firm_name = None
#         self._unit_of_measurement = currency

#     @property
#     def name(self):
#         """Return the name of the sensor."""
#         return self._name

#     @property
#     def state(self):
#         """Return the state of the sensor."""
#         return self._state

#     @property
#     def unit_of_measurement(self):
#         """Return the unit of measurement this sensor expresses itself in."""
#         return self._unit_of_measurement

#     @property
#     def icon(self):
#         """Return the icon to use in the frontend."""
#         return ACCOUNT_ICON

#     @property
#     def device_state_attributes(self):
#         """Return the state attributes of the sensor."""
#         return {
#             ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
#             ATTR_FIRM_NAME: self._firm_name,
#             ATTR_ACCT_TYPE: self._acct_type,
#             ATTR_CATEGORY: self._category
#         }

#     def update(self):
#         """Get the latest state of the sensor."""
#         self._personal_capital_data.update()
#         for account in self._personal_capital_data:
#             if self._name == "Personal Capital {}".format(account['name']):
#                 self._state = account['balance']
#                 self._firm_name = account['firmName']
#                 self._acct_type = account['accountType']
#                 self._category = account['productType']
#                 self._unit_of_measurement = account['currency']
