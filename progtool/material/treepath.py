from __future__ import annotations
from typing import Any


class TreePath:
    __parts: tuple[str, ...]

    def __init__(self, *parts: str):
        self.__parts = parts

    def __truediv__(self, part: str) -> TreePath:
        return TreePath(*self.__parts, part)

    @property
    def parts(self) -> tuple[str, ...]:
        return self.__parts

    def __str__(self):
        return ",".join(self.__parts)

    def __repr__(self):
        argument_string = ", ".join(map(repr, self.__parts))
        return f'TreePath({argument_string})'

    def __hash__(self):
        return hash(self.__parts)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TreePath):
            return self.parts == other.parts
        else:
            return NotImplemented
