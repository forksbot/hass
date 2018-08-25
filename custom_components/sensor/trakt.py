"""
A component which allows you to get information from Trakt.

For more details about this component, please refer to the documentation at
https://github.com/custom-components/sensor.trakt
"""
import logging
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.components.http import HomeAssistantView
from homeassistant.const import (CONF_NAME)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['trakt.py==2.14.1']

DEPENDENCIES = ['http']

_LOGGER = logging.getLogger(__name__)

SCOPE = 'user-read-playback-state user-modify-playback-state user-read-private'
DEFAULT_CACHE_PATH = '.trakt-token-cache'
AUTH_CALLBACK_PATH = '/api/trakt'
AUTH_CALLBACK_NAME = 'api:trakt'
ICON = 'mdi:filmstrip'
DOMAIN = 'trakt'
CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_SECRET = 'client_secret'
CONF_USERNAME = 'username'
CONF_CACHE_PATH = 'cache_path'
CONFIGURATOR_LINK_NAME = 'Link Trakt account'
CONFIGURATOR_SUBMIT_CAPTION = 'I authorized successfully'
CONFIGURATOR_DESCRIPTION = 'To link your Trakt account, ' \
                           'click the link, login, and authorize:'

WATCHLIST_MOVIES = 'trakt_watchlist_movies'

__version__ = '0.0.1'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CLIENT_ID): cv.string,
    vol.Required(CONF_CLIENT_SECRET): cv.string,
    vol.Optional(CONF_CACHE_PATH): cv.string
})

SCAN_INTERVAL = timedelta(seconds=300)

def request_app_setup(hass, config, trakt, add_devices, discovery_info=None):
    """Request configuration steps from the user."""
    from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
    configurator = hass.components.configurator

    def trakt_configuration_callback(data):
        """Run when the configuration callback is called."""
        from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, data.get('verification_code'))
        result = pc.authenticate_password(config.get(CONF_PASSWORD))

        if result == RequireTwoFactorException:
            configurator.notify_errors(_CONFIGURING['personalcapital'], "Invalid verification code")
        else:
            continue_setup_platform(hass, config, pc, add_devices, discovery_info)

    if 'personalcapital' not in _CONFIGURING:
        try:
            pc.login(config.get(CONF_EMAIL), config.get(CONF_PASSWORD))
        except RequireTwoFactorException:
            pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)

    _CONFIGURING['personalcapital'] = configurator.request_config(
        'Personal Capital',
        personalcapital_configuration_callback,
        description="Verification code sent to phone",
        submit_caption='Verify',
        fields=[{
            'id': 'verification_code',
            'name': "Verification code",
            'type': 'string'}]
    )

def request_configuration(hass, config, Trakt):
    """Request Trakt authorization."""
    configurator = hass.components.configurator
    
    oauth = Trakt['oauth'].authorize_url(callback_url, 'code', None, config.get(CONF_USERNAME))
    
    hass.data[DOMAIN] = configurator.request_config(
        DEFAULT_NAME, lambda _: None,
        link_name=CONFIGURATOR_LINK_NAME,
        link_url="https://api.trakt.tv/auth/signin",
        description=CONFIGURATOR_DESCRIPTION,
        submit_caption=CONFIGURATOR_SUBMIT_CAPTION)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Trakt platform."""
    from trakt import Trakt
    callback_url = '{}{}'.format(hass.config.api.base_url, AUTH_CALLBACK_PATH)
    cache = config.get(CONF_CACHE_PATH, hass.config.path(DEFAULT_CACHE_PATH))
    
    Trakt.configuration.defaults.client(
        id=config.get(CONF_CLIENT_ID),
        secret=config.get(CONF_CLIENT_SECRET)
    )
    
    oauth = Trakt['oauth'].token_refresh(cache, callback_url)
    
    if not oauth or not oauth.get('access_token'):
         _LOGGER.info("no token; requesting authorization")
        hass.http.register_view(TraktAuthCallbackView(config, add_devices, oauth))
        request_configuration(hass, config, add_devices, Trakt)
        return
    
    Trakt.configuration.defaults.oauth.from_response(oauth)
    
    if hass.data.get(DOMAIN):
        configurator = hass.components.configurator
        configurator.request_done(hass.data.get(DOMAIN))
        del hass.data[DOMAIN]
        
    add_devices([TraktWatchlistSensor(Trakt)], True)

# trakt.calendars.my.shows()
# trakt.sync.watchlist.get()
class TraktAuthCallbackView(HomeAssistantView):
    """Trakt Authorization Callback View."""

    requires_auth = False
    url = AUTH_CALLBACK_PATH
    name = AUTH_CALLBACK_NAME

    def __init__(self, config, add_devices, oauth):
        """Initialize."""
        self.config = config
        self.add_devices = add_devices
        self.oauth = oauth

    @callback
    def get(self, request):
        """Receive authorization token."""
        hass = request.app['hass']
        if not self.oauth or not self.oauth.get('access_token'):
            _LOGGER.error('ERROR: oauth failed')
            exit(1)
        self.oauth.get_access_token(request.query['code'])
        hass.async_add_job(setup_platform, hass, self.config, self.add_devices)

class TraktWatchlistSensor(Entity):
    def __init__(self, hass, Trakt):
        from trakt import Trakt
        self._trakt = Trakt
        self._state = None
        self.hass.data[WATCHLIST_MOVIES] = {}
        # self._watchlist_shows = {}
        self.update()

    def update(self):
        movies = self._trakt['sync/watchlist'].movies()
        if not movies :
            return False
        else:
            self._state = len(movies)
            for movie in movies['items']:
                self.hass.data[WATCHLIST_MOVIES][movie.title] = {
                    "movie_year": movie.year,
                }

        # shows = self._trakt['sync/watchlist'].shows()
        # if not shows :
        #     return False
        # else:
        #     for show in shows['items']:
        #         self._watchlist_shows[show.title] = {
        #             "show_year": show.year,
        #         }

    @property
    def name(self):
        return 'Trakt Watchlist'

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        return self.hass.data[WATCHLIST_MOVIES]
