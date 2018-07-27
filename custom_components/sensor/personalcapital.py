"""
Support for Personal Capital sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.personalcapital/
"""
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

ATTR_FIRM_NAME = "Firm name"
ATTR_ACCT_TYPE = "Account type"
ATTR_CATEGORY = 'Category'

ACCOUNT_ICON = 'mdi:coin'
BUDGET_ICON = 'mdi:coin'
TRANSACTIONS_ICON = 'mdi:coin'
NET_WORTH_ICON = 'mdi:coin'

CONF_ATTRIBUTION = "Data provided by personalcapital.com"

DATA_PERSONAL_CAPITAL = 'personalcapital_cache'
DEPENDENCIES = ['personalcapital']

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Personal Capital sensors."""
    if discovery_info is None:
        return
    if 'account' in discovery_info:
        account = discovery_info['account']
        sensor = AccountSensor(hass.data[DATA_PERSONAL_CAPITAL], account['name'], account['currency'])
    if 'networth' in discovery_info:
        networth = discovery_info['networth']
        sensor = NetWorthSensor(hass.data[DATA_PERSONAL_CAPITAL], networth['networth'], networth['assets'], networth['liabilities'], networth['investmentAccountsTotal'], networth['mortgageAccountsTotal'], networth['cashAccountsTotal'], networth['otherAssetAccountsTotal'], networth['otherLiabilitiesAccountsTotal'], networth['creditCardAccountsTotal'], networth['loanAccountsTotal'])

    add_devices([sensor], True)

class NetWorthSensor(Entity):
    """Representation of a personalcapital.com sensor."""

    def __init__(self, personal_capital_data, name, currency):
        """Initialize the sensor."""
        self._personal_capital_data = personal_capital_data
        self._name = "Personal Capital Networth"
        self._state = None
        self._assets = None
        self._liabilities = None
        self._investments = None
        self._mortgages = None
        self._cash = None
        self._otherAssets = None
        self._otherLiabilities = None
        self._creditCards = None
        self._loans = None
        self._unit_of_measurement = "USD"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ACCOUNT_ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
            ATTR_ASSETS: self._assets,
            ATTR_LIABILITIES: self._liabilities,
            ATTR_INVESTMENTS: self._investments,
            ATTR_MORTGAGES: self._mortgages,
            ATTR_CASH: self._cash,
            ATTR_OTHER_ASSETS: self._otherAssets,
            ATTR_OTHER_LIABILITIES: self._otherLiabilities,
            ATTR_CREDIT_CARDS: self._creditCards,
            ATTR_LOANS: self._loans
        }

    def update(self):
        """Get the latest state of the sensor."""
        self._personal_capital_data.update()
        self._state = account.networth
        self._assets = self._personal_capital_data.assets
        self._liabilities = self._personal_capital_data.liabilities
        self._investments = self._personal_capital_data.investmentAccountsTotal
        self._mortgages = self._personal_capital_data.mortgageAccountsTotal
        self._cash = self._personal_capital_data.cashAccountsTotal
        self._otherAssets =self._personal_capital_data.otherAssetAccountsTotal
        self._otherLiabilities = self._personal_capital_data.otherLiabilitiesAccountsTotal
        self._creditCards = self._personal_capital_data.creditCardAccountsTotal
        self._loans = self._personal_capital_data.loanAccountsTotal

class AccountSensor(Entity):
    """Representation of a personalcapital.com sensor."""

    def __init__(self, personal_capital_data, name, currency):
        """Initialize the sensor."""
        self._personal_capital_data = personal_capital_data
        self._name = "Personal Capital {}".format(name)
        self._state = None
        self._acct_type = None
        self._category = None
        self._firm_name = None
        self._unit_of_measurement = currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ACCOUNT_ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
            ATTR_FIRM_NAME: self._firm_name,
            ATTR_ACCT_TYPE: self._acct_type,
            ATTR_CATEGORY: self._category
        }

    def update(self):
        """Get the latest state of the sensor."""
        self._personal_capital_data.update()
        for account in self._personal_capital_data:
            if self._name == "Personal Capital {}".format(account['name']):
                self._state = account['balance']
                self._firm_name = account['firmName']
                self._acct_type = account['accountType']
                self._category = account['productType']
                self._unit_of_measurement = account['currency']