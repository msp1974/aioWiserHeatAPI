import json
from os.path import exists

import aiofiles

from ..exceptions import WiserExtraConfigError


class _WiserExtraConfig:
    def __init__(self, config_file: str, hub_name: str):
        self._config_file = config_file + "_" + hub_name
        self._config = {}

    async def async_load_config(self):
        if exists(self._config_file):
            async with aiofiles.open(self._config_file, mode="r") as config_file:
                try:
                    contents = await config_file.read()
                    if contents:
                        self._config = json.loads(contents)
                except (
                    OSError,
                    EOFError,
                    TypeError,
                    AttributeError,
                    json.JSONDecodeError,
                ) as ex:
                    raise WiserExtraConfigError("Error loading extra config file") from ex
        else:
            await self.async_update_config("Info", "Version", "1.0.0")
        return

    async def async_update_config(self, section: str, key: str, value):
        # If section doesn't exist
        if section not in self._config:
            self._config[section] = {}

        # If key not in section
        if key and value:
            if self._config[section].get(key):
                self._config[section][key].update(value)
            else:
                self._config[section][key] = value

        await self.async_write_config()

    async def async_remove_config(self, section: str, key: str):
        if key and self._config[section].get(key):
            del self._config[section][key]

        await self.async_write_config()

    async def async_write_config(self):
        # Write to config file
        async with aiofiles.open(self._config_file, mode="w") as config_file:
            try:
                await config_file.write(json.dumps(self._config, indent=2))
            except (
                OSError,
                EOFError,
                TypeError,
                AttributeError,
                json.JSONDecodeError,
            ) as ex:
                raise WiserExtraConfigError("Error writing to extra config file") from ex

    # @property
    def config(self, section: str = None, key: str = None):
        try:
            if section:
                if key:
                    return self._config[section][key]
                else:
                    return self._config[section]
            else:
                return self._config
        except:
            return None
