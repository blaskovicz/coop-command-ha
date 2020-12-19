# https://github.com/blaskovicz/coop-command/blob/master/coop-command/coop-command.ino#L520

import logging
import aiohttp
import asyncio

_LOGGER = logging.getLogger(__name__)


class APILight:
    def __init__(self, base_url, path, name=None):
        if name is None:
            name = path
        self.id = path
        self._base_url = base_url

        # default to red
        self.r = 255.0
        self.g = 14.0
        self.b = 14.0

        self.on = False
        self._path = path
        self.name = name

    async def save(self):
        on = "true" if self.on else "false"
        data = {'r': self.r, 'g': self.g, 'b': self.b, 'on': on}

        _LOGGER.debug(f'saving light {self.name} to {data}')

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self._base_url}/{self._path}', data=data) as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Put light failure at {self._base_url}/{self._path}: {res.status} {text}')
                return await res.json()

    async def update(self):
        _LOGGER.debug(f'updating light {self.name} data')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self._base_url}/{self._path}') as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Light info fetch failure at {self._base_url}/{self._path}: {res.status} {text}')

                data = await res.json()

                _LOGGER.debug(f'light {self.name} data is now {data}')

                self.r = float(data['r'])
                self.g = float(data['g'])
                self.b = float(data['b'])
                self.on = data['on']


class API:
    def __init__(self, host):
        self._base_url = f'http://{host}/api'

    async def sensor_info(self):
        _LOGGER.debug('fetching sensor info')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self._base_url}/dht') as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Sensor info fetch failure at {self._base_url}/dht: {res.status} {text}')
                data = await res.json()
                _LOGGER.debug(f'sensor info is now {data}')
                return data

    async def hardware_info(self):
        _LOGGER.debug('fetching hardware info')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self._base_url}/_info') as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Hardware info fetch failure at {self._base_url}/_info: {res.status} {text}')
                data = await res.json()
                _LOGGER.debug(f'hardware info is now {data}')
                return data

    async def door_info(self):
        _LOGGER.debug('fetching door data')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self._base_url}/doors') as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Doors fetch failure at {self._base_url}/doors: {res.status} {text}')
                data = await res.json()
                _LOGGER.debug(f'door data is now {data}')
                return data

    # TODO make api door class and use like api light
    async def save_doors(self, state):
        data = {}
        for door_id in state:
            val = state[door_id]
            data[door_id] = "true" if val else "false"

        _LOGGER.debug(f'saving doors data {data}')
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self._base_url}/doors', data=data) as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Put light failure at {self._base_url}/doors: {res.status} {text}')
                return await res.json()

    def lights(self):
        return [
            APILight(self._base_url, 'leds', 'Coop LEDs')
        ]
