"""Coop Command integration"""

# based on https://github.com/sampsyo/hass-smartthinq/blob/master/__init__.py

from .api import API
from homeassistant.const import CONF_HOST
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging
from .const import DOMAIN


COOP_COMMAND_COMPONENTS = [
    'light',
    'cover',
    # 'sensor', # TODO
]

_LOGGER = logging.getLogger(__name__)

# require a top-level schema with host:
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    if DOMAIN not in config:
        raise Exception(f'direct use of {DOMAIN} component is unsupported without extra config')

    # TODO sanatize and normalize here
    hass.data[CONF_HOST] = config[DOMAIN].get(CONF_HOST)

    # healthcheck
    API(hass.data[CONF_HOST]).hardware_info()

    # let other components that use the API load
    for component in COOP_COMMAND_COMPONENTS:
        _LOGGER.info(f"loading component {component}")
        await hass.helpers.discovery.async_load_platform(component, DOMAIN, {}, config)

    return True
