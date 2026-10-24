import asyncio
from pathlib import Path


async def file_exists(file: str) -> bool:
    """Return whether a path is a file without blocking the event loop."""
    return await asyncio.to_thread(Path(file).is_file)


def is_value_in_list(value: str, item_list: list) -> bool:
    for item in item_list:
        if value.casefold() == item.casefold():
            return True
    return False


def is_valid_level(level: int) -> bool:
    if level >= 0 and level <= 100:
        return True
    return False
