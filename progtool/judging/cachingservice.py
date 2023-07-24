import asyncio
import logging
from progtool.content.tree import ContentNode, Exercise
import json

from progtool.judging.judgment import Judgment
from progtool import settings


class CachingService:
    __root: ContentNode

    __event_loop: asyncio.AbstractEventLoop

    __dirty: bool

    def __init__(self, root: ContentNode, event_loop: asyncio.AbstractEventLoop):
        self.__root = root
        self.__event_loop = event_loop
        self.__dirty = False

        self.__load_cache(root)
        self.__observe_nodes(root)

    def __load_cache(self, root: ContentNode):
        data = self.__load_cache_data()
        for exercise in root.exercises:
            path = str(exercise.tree_path)
            if path in data:
                exercise.judgment = Judgment[data[path]]

    def __load_cache_data(self) -> dict[str, str]:
        path = settings.judgment_cache()
        if path.is_file():
            logging.info('Cache found; loading data')
            with path.open() as file:
                return json.load(file)
        else:
            logging.info('No cache found')
            return {}

    def write_cache(self):
        data = self.__collect_judgments()
        self.__write_cache_data(data)

    def __collect_judgments(self) -> dict[str, str]:
        data = {}
        for exercise in self.__root.exercises:
            if exercise.judgment is not Judgment.UNKNOWN:
                data[str(exercise.tree_path)] = str(exercise.judgment)
        return data

    def __write_cache_data(self, data: dict[str, str]) -> None:
        with settings.judgment_cache().open('w') as file:
            json.dump(data, file, sort_keys=True, indent=4)

    def __observe_nodes(self, root: ContentNode) -> None:
        def observer():
            if not self.__dirty:
                self.__dirty = True
                self.__schedule_write()
        for exercise in root.exercises:
            exercise.observe_judgment(observer)

    def __schedule_write(self) -> None:
        def write_after_delay():
            self.__event_loop.call_later(settings.cache_delay(), self.write_cache)
        self.__event_loop.call_soon_threadsafe(write_after_delay)
