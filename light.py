"""Platform for light integration."""
import logging
from homeassistant.components.light import (
    SUPPORT_COLOR, ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, ATTR_HS_COLOR, LightEntity, ENTITY_ID_FORMAT)
from homeassistant.const import CONF_HOST
import homeassistant.util.color as color_util

from .api import API

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the light platform."""

    api = API(hass.data.get(CONF_HOST))

    # Add devices
    async_add_entities((CoopCommandLight(light) for light in api.lights()), True)


# example from https://github.com/sampsyo/hass-smartthinq/blob/master/climate.py
class CoopCommandLight(LightEntity):
    """Representation of a Coop Command Light."""

    def __init__(self, light):
        """Initialize our light."""
        super().__init__()
        self._light = light
        self.entity_id = ENTITY_ID_FORMAT.format(light.id)

    @property
    def hs_color(self):
        """Return the hs_color of the light."""
        # return tuple(map(int, self.tuya.hs_color()))
        return color_util.color_RGB_to_hs(self._light.r, self._light.g, self._light.b)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_COLOR
        # supports = SUPPORT_BRIGHTNESS
        # if self.tuya.support_color():
        #     supports = supports | SUPPORT_COLOR
        # if self.tuya.support_color_temp():
        #     supports = supports | SUPPORT_COLOR_TEMP
        # return supports

    @property
    def name(self):
        """Return the display name of this light."""
        return self._light.name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._light.on

    # https://github.com/andrewmyhre/home-assistant-config/blob/master/tuya.py#L75
    async def async_turn_on(self, **kwargs):
        """Instruct the light to set its color or turn on."""
        if (ATTR_BRIGHTNESS not in kwargs
                and ATTR_HS_COLOR not in kwargs
                and ATTR_COLOR_TEMP not in kwargs):
            self._light.on = True
            await self._light.save()
            return
        # if ATTR_BRIGHTNESS in kwargs and ATTR_HS_COLOR in kwargs:
        #     self.tuya.set_color([kwargs[ATTR_HS_COLOR][0], kwargs[ATTR_HS_COLOR][1], kwargs[ATTR_BRIGHTNESS]])
        #     return
        # if ATTR_BRIGHTNESS in kwargs:
        #     self.tuya.set_brightness(kwargs[ATTR_BRIGHTNESS])
        if ATTR_HS_COLOR in kwargs:
            hs_color = kwargs[ATTR_HS_COLOR]
            rgb = color_util.color_hs_to_RGB(*hs_color)
            self._light.r = rgb[0]
            self._light.g = rgb[1]
            self._light.b = rgb[2]
            await self._light.save()
            return
        # if ATTR_COLOR_TEMP in kwargs:
        #     color_temp = colorutil.color_temperature_mired_to_kelvin(
        #         kwargs[ATTR_COLOR_TEMP])
        #     self.tuya.set_color_temp(color_temp)

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.on = False
        await self._light.save()

    async def async_update(self):
        """Fetch new state data for this light."""
        await self._light.update()
