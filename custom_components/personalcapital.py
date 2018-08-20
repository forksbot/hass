"""
Support for Personal Captial.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/personalcapital/
"""
from datetime import timedelta
import logging
import json

import voluptuous as vol

from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.util import Throttle

# const ENDPOINTS = {
#     //Fetch
#     "getCategories" : "/api/transactioncategory/getCategories",
#     "getUserMessages" : "/api/message/getUserMessages",
#     "getAccounts" : "/api/newaccount/getAccounts2",
#     "getAdvisor" : "/api/profile/getAdvisor",
#     "getFunnelAttributes" : "/api/profile/getFunnelAttributes",
#     "getPerson" : "/api/person/getPerson",
#     "getHistories" : "/api/account/getHistories",
#     "getUserSpending" : "/api/account/getUserSpending",
#     "getRetirementCashFlow" : "/api/account/getRetirementCashFlow",
#     "getQuotes" : "/api/invest/getQuotes",
#     "getHoldings" : "/api/invest/getHoldings",
#     "searchSecurity" : "/api/invest/searchSecurity",
#     "getUserTransactions" : "/api/transaction/getUserTransactions",
#     "getCustomProducts" : "/api/search/getCustomProducts"
# };

REQUIREMENTS = ['personalcapital==1.0.1']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'personalcapital'

CONF_EMAIL = 'email'
CONF_PASSWORD = 'password'
CONF_OPTIONS = 'options'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)

DATA_PERSONAL_CAPITAL = 'personalcapital_cache'

PERSONAL_CAPITAL_SESSION_FILE = '.personal_capital.session'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_OPTIONS, default=[]):
            vol.All(cv.ensure_list, [cv.string])
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Personal Capital component.

    Will automatically setup sensors to support accounts discovered.
    """
    email = config[DOMAIN].get(CONF_EMAIL)
    password = config[DOMAIN].get(CONF_PASSWORD)
    options = config[DOMAIN].get(CONF_OPTIONS)

    hass.data[DATA_PERSONAL_CAPITAL] = personal_capital_data = PersonalCapitalData(email, password, hass.config.path(PERSONAL_CAPITAL_SESSION_FILE))

    if 'accounts' in options:
        for account in personal_capital_data.accountDetails['accounts']:
            load_platform(hass, 'sensor', DOMAIN, {'account': account}, config)

    if 'networth' in options:
        load_platform(hass, 'sensor', DOMAIN, {'networth': personal_capital_data.accountDetails}, config)

    return True


class PersonalCapitalData(object):
    """Get the latest data and update the states."""

    def __init__(self, email, password, session_path):
        """Init the personalcapital data object."""
        import personalcapital
        self.pc = PersonalCapital()
        self.email = email
        self.password = password
        self._session_path = session_path

        self.update()

    def load_session(self):
        if not os.path.isfile(self._session_path):
            return

        try:
            with open(self._session_path) as data_file:    
                cookies = {}
                try:
                    cookies = json.load(data_file)
                except ValueError as err:
                    logging.error(err)
                self.set_session(cookies)
        except IOError as err:
            logging.error(err)

    def save_session(self):
        save_json(self._session_path, self.pc.get_session())

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Personal Capital."""

        self.load_session()

        try:
            self.pc.login(self.email, self.password)
        except RequireTwoFactorException:
            # setup(); #TODO

            self.pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)

            # hass.components.persistent_notification.create(
            #     'In order to authorize Home-Assistant to view your calendars '
            #     'you must visit: <a href="{}" target="_blank">{}</a> and enter '
            #     'code: {}'.format(dev_flow.verification_url,
            #                     dev_flow.verification_url,
            #                     dev_flow.user_code),
            #     title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID
            # )

            # self.pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input('code: ')) # How to get code from front-end?
            # self.pc.authenticate_password(self.password)

        self.save_session()

        # TODO ERROR HANDLING "<Response [200]>"
        self.accountDetails = self.pc.fetch('/newaccount/getAccounts').json()['spData']