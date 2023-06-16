from __future__ import annotations


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
