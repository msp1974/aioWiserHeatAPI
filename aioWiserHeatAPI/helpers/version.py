"""Version helpers."""

from dataclasses import dataclass


@dataclass
class Version:
    """Class to handle PEP440 versions."""

    version: str

    def __gt__(self, other):
        if isinstance(other, Version):
            return (
                self.major >= other.major
                and self.minor >= other.minor
                and self.micro > other.micro
            )

    def __ge__(self, other):
        if isinstance(other, Version):
            return self.__eq__(other) or self.__gt__(other)

    def __lt__(self, other):
        if isinstance(other, Version):
            return (
                self.major <= other.major
                and self.minor <= other.minor
                and self.micro < other.micro
            )

    def __le__(self, other):
        if isinstance(other, Version):
            return self.__eq__(other) or self.__lt__(other)

    def __eq__(self, other):
        if isinstance(other, Version):
            return (
                self.major == other.major
                and self.minor == other.minor
                and self.micro == other.micro
            )

    @property
    def major(self) -> int:
        """Get major version."""
        try:
            return self.version.split(".")[0]
        except IndexError:
            return None

    @property
    def minor(self) -> int:
        """Get minor version."""
        try:
            return self.version.split(".")[1]
        except IndexError:
            return None

    @property
    def micro(self) -> int:
        """Get micro version."""
        try:
            full_micro = self.version.split(".")[2]
            return full_micro.split("-")[0]
        except IndexError:
            return None
