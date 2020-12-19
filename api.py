# https://github.com/blaskovicz/coop-command/blob/master/coop-command/coop-command.ino#L520
import requests
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
        self.r = 0.0
        self.g = 0.0
        self.b = 0.0
        self.on = False
        self._path = path
        self.name = name

    async def save(self):
        on = "true" if self.on else "false"
        data = {'r': self.r, 'g': self.g, 'b': self.b, 'on': on}

        _LOGGER.info(f'saving light {self.name} to {data}')

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self._base_url}/{self._path}', data=data) as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Put light failure at {self._base_url}/{self._path}: {res.status} {text}')
                return await res.json()

    async def update(self):
        _LOGGER.info(f'updating light {self.name} data')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self._base_url}/{self._path}') as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Light info fetch failure at {self._base_url}/{self._path}: {res.status} {text}')

                data = await res.json()

                _LOGGER.info(f'light {self.name} data is now {data}')
                self.r = float(data['r'])
                self.g = float(data['g'])
                self.b = float(data['b'])
                self.on = data['on']


class API:
    def __init__(self, host):
        self._base_url = f'http://{host}/api'

    def hardware_info(self):
        res = requests.get(f'{self._base_url}/_info')
        if res.status_code != 200:
            raise Exception(f'Hardware info fetch failure at {self._base_url}/_info: {res.status_code} {res.text}')
        return res.json()

    async def door_info(self):
        _LOGGER.info(f'fetching door data')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self._base_url}/doors') as res:
                if res.status != 200:
                    text = await res.text()
                    raise Exception(f'Doors fetch failure at {self._base_url}/doors: {res.status} {text}')
                data = await res.json()
                _LOGGER.info(f'door data is now {data}')
                return data

    # TODO make api door class and use like api light
    async def save_doors(self, state):
        data = {}
        for door_id in state:
            val = state[door_id]
            data[door_id] = "true" if val else "false"

        _LOGGER.info(f'saving doors data {data}')
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
