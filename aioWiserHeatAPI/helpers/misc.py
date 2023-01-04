from pathlib import Path, _ignore_error as pathlib_ignore_error
from typing import Union

import aiofiles.os as os
import enum


async def file_exists(file: str) -> bool:
    return await os.path.isfile(file)


def is_value_in_list(value: str, item_list: list) -> bool:
    for item in item_list:
        if value.casefold() == item.casefold():
            return True
    return False


def is_valid_level(level: int) -> bool:
    if level >= 0 and level <= 100:
        return True
    return False
