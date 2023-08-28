from __future__ import annotations
from functools import total_ordering
from typing import Any
import re


@total_ordering
class Version:
    __major: int
    __minor: int
    __patch: int

    @staticmethod
    def parse(string: str) -> Version:
        regex = r'v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
        if match := re.fullmatch(regex, string):
            groups = match.groupdict()
            major = int(groups['major'])
            minor = int(groups['minor'])
            patch = int(groups['patch'])
            return Version(major, minor, patch)
        else:
            raise VersionException(f'Could not parse {string}')


    def __init__(self, major: int, minor: int, patch: int):
        self.__major = major
        self.__minor = minor
        self.__patch = patch

    @property
    def major(self) -> int:
        return self.__major

    @property
    def minor(self) -> int:
        return self.__minor

    @property
    def patch(self) -> int:
        return self.__patch

    @property
    def triple(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Version):
            return self.triple == other.triple
        else:
            return NotImplemented

    def __lt__(self, other: Version) -> bool:
        return self.triple < other.triple

    def __str__(self) -> str:
        return f"v{'.'.join(str(n) for n in self.triple)}"


class VersionException(Exception):
    pass
