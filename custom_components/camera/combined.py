"""
A camera platform that give you a combined feed of your defined camera entities.

For more details about this component, please refer to the documentation at
https://github.com/custom-components/camera.combined
"""
import logging
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.camera import (PLATFORM_SCHEMA, Camera)

__version__ = '0.0.1'
_LOGGER = logging.getLogger(__name__)

CONF_ENTITIES = 'entities'
CONF_BASE_ADDRESS = 'base_address'
CONF_NAME = 'name'

DEFAULT_NAME = 'Combined'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_BASE_ADDRESS): cv.string,
    vol.Required(CONF_ENTITIES):
        vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Camera that works with local files."""
    entities = config.get(CONF_ENTITIES)
    name = config.get(CONF_NAME)
    base_address = config.get(CONF_BASE_ADDRESS)
    camera = CombinedhCamera(hass, name, entities, base_address)
    add_devices([camera])


class CombinedhCamera(Camera):
    """Representation of the camera."""

    def __init__(self, hass, name, entities, base_address):
        """Initialize Unsplash Camera component."""
        super().__init__()
        self.hass = hass
        self.is_streaming = False
        self._name = name
        self._base_address = base_address
        self._entities = entities
        self._total = len(entities)
        self._count = 0

    def camera_image(self):
        """Return image response."""
        camera = self._entities[self._count]
        state = self.hass.states.get(camera)
        attribute = state.attributes.get('entity_picture')
        feed = requests.get(self._base_address + attribute).content
        if self._count == (self._total - 1):
            self._count = 0
        else:
            self._count = self._count + 1
        return feed

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name