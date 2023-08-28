import abc
from typing import Generic, TypeVar


T = TypeVar('T')
E = TypeVar('E')


class Result(abc.ABC, Generic[T, E]):
    pass


class Success(Result[T, E]):
    __result: T

    def __init__(self, result: T):
        self.__result = result

    @property
    def result(self) -> T:
        return self.__result


class Failure(Result[T, E]):
    __error: E

    def __init__(self, error: E):
        self.__error = error

    @property
    def error(self) -> E:
        return self.__error
