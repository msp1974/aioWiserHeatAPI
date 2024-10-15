"""Version helpers."""

from dataclasses import dataclass


@dataclass
class Version:
    """Class to handle PEP440 versions."""

    version: str

    def __gt__(self, other):
        if isinstance(other, Version):
            return self._version_compare(self.version, other.version) == 1

    def __ge__(self, other):
        if isinstance(other, Version):
            return self.__eq__(other) or self.__gt__(other)

    def __lt__(self, other):
        if isinstance(other, Version):
            return self._version_compare(self.version, other.version) == -1

    def __le__(self, other):
        if isinstance(other, Version):
            return self.__eq__(other) or self.__lt__(other)

    def __eq__(self, other):
        if isinstance(other, Version):
            return self._version_compare(self.version, other.version) == 0

    def _version_compare(self, v1: str, v2: str) -> int:
        version1 = v1.replace("-", ".").split(".")
        version2 = v2.replace("-", ".").split(".")

        length = max(len(version1), len(version2))

        # Compare each component of the version strings.
        for i in range(length):
            v1_itm = int(version1[i]) if version1[i].isdigit() else version1[i]
            v2_itm = int(version2[i]) if version2[i].isdigit() else version2[i]

            if v1_itm > v2_itm:
                return 1
            if v1_itm < v2_itm:
                return -1

        return 0
