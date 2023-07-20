from enum import Enum


class Judgment(Enum):
    UNKNOWN = 0
    PASS = 1
    FAIL = -1

    def __str__(self):
        return self.name
