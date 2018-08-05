"""
A component which allows you to get information from Trakt.

For more details about this component, please refer to the documentation at
https://github.com/custom-components/sensor.trakt
"""
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (PLATFORM_SCHEMA)

REQUIREMENTS = ['trakt.py==2.14.1']

CONF_ID = 'id'
CONF_SECRET = 'secret'

WATCHLIST_MOVIES = 'trakt_watchlist_movies'

SCAN_INTERVAL = timedelta(seconds=120)

ICON = 'mdi:movie-roll'
__version__ = '0.0.1'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID): cv.string,
    vol.Required(CONF_SECRET): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    api_id = config.get(CONF_ID)
    api_secret = config.get(CONF_SECRET)
    add_devices([TraktWatchlistSensor(hass,api_id, api_secret)])

class TraktWatchlistSensor(Entity):
    def __init__(self, hass, api_id, api_secret):
        from trakt import Trakt
        self._trakt = Trakt
        self._trakt.configuration.defaults.client(
            id=api_id,
            secret=api_secret
        )
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
