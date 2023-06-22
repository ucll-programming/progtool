from pathlib import Path
import abc
from typing import Literal
import pydantic


class Judge(abc.ABC):
    @abc.abstractmethod
    async def judge(self) -> bool:
        ...


class JudgeMetadata(pydantic.BaseModel):
    type: Literal['pytest']
    file: str


class JudgeError(Exception):
    pass

