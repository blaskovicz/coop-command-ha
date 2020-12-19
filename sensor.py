"""Platform for cover integration."""
import logging
import async_timeout
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_HOST, TEMP_FAHRENHEIT, PERCENTAGE
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
    """Set up the sensor platform."""

    api = API(hass.data.get(CONF_HOST))

    async def async_update_data():
        """Fetch all data for info under this endpoint, in bulk"""
        async with async_timeout.timeout(10):
            return await api.sensor_info()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name=f'{DOMAIN}.sensor',
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    # Add sensors
    async_add_entities([CoopCommandTemperatureSensor(coordinator), CoopCommandHumiditySensor(coordinator)])

# https://developers.home-assistant.io/docs/core/entity/sensor/
# https://github.com/home-assistant/example-custom-config/blob/7f5a5b20003f6634967ee3a273011b131142339a/custom_components/example_sensor/sensor.py


class CoopCommandTemperatureSensor(CoordinatorEntity, Entity):
    """Representation of a Coop Command temperature sensor."""

    def __init__(self, coordinator):
        """Initialize our sensor."""
        super().__init__(coordinator)
        self._name = 'temperature'

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for this sensor."""
        return TEMP_FAHRENHEIT

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._name]


class CoopCommandHumiditySensor(CoordinatorEntity, Entity):
    """Representation of a Coop Command humidity sensor."""

    def __init__(self, coordinator):
        """Initialize our sensor."""
        super().__init__(coordinator)
        self._name = 'humidity'

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for this sensor."""
        return PERCENTAGE

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._name]
