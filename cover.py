"""Platform for cover integration."""
import logging
import async_timeout
from homeassistant.helpers.entity import async_generate_entity_id
from datetime import timedelta
from homeassistant.components.cover import (CoverEntity, DEVICE_CLASS_DOOR, SUPPORT_CLOSE, SUPPORT_OPEN, ENTITY_ID_FORMAT)
from homeassistant.const import CONF_HOST
import homeassistant.util.color as color_util
from .const import DOMAIN
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import API

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the cover platform."""

    api = API(hass.data.get(CONF_HOST))

    async def async_update_data():
        """Fetch all data for devices under this endpoint, in bulk"""
        async with async_timeout.timeout(10):
            return await api.door_info()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name=f'{DOMAIN}.cover',
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    # Add devices
    async_add_entities(CoopCommandDoor(coordinator, api, door_id) for door_id in coordinator.data)

# https://developers.home-assistant.io/docs/core/entity/cover

# Currently we have a "dumb" door that may be in some nknown state.
# We have no sensors yet to know if we're openeing or closing (or if it's open or closed)
# so we must make an assumption based on direction of motion since the door stops when it
# reaches the end of the track


class CoopCommandDoor(CoordinatorEntity, CoverEntity):
    """Representation of a Coop Command Door."""

    def __init__(self, coordinator, api, door_id):
        """Initialize our door."""
        super().__init__(coordinator)
        self.entity_id = ENTITY_ID_FORMAT.format(door_id)
        self._door_id = door_id
        self._api = api

    @ property
    def name(self):
        """Return the display name of this door."""
        return self._door_id

    @ property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE

    @ property
    def device_class(self):
        """What type of device is this."""
        return DEVICE_CLASS_DOOR

    def is_closed(self):
        """If the door is closed or not."""
        val = self.coordinator.data[self._door_id]
        typ = type(val)
        if typ != bool:
            raise Exception(f'unexpected data type for door {self.name} {val}: {typ}')
        # api considers True -> open, False -> closed
        return not val

    async def save_doors(self):
        await self._api.save_doors(self.coordinator.data)
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs):
        """Close the door."""
        self.coordinator.data[self._door_id] = False
        await self.save_doors()

    async def async_open_cover(self, **kwargs):
        """Open the door."""
        self.coordinator.data[self._door_id] = True
        await self.save_doors()
