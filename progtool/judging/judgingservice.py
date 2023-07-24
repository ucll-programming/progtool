import asyncio
import logging
from progtool.content.tree import ContentNode, Exercise
import json

from progtool.judging.judgment import Judgment
from progtool import settings


class JudgingService:
    __event_loop: asyncio.AbstractEventLoop

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.__event_loop = event_loop

    def judge(self, exercise: Exercise) -> None:
        async def perform_judging():
            logging.info(f'Judging {exercise.tree_path}')
            judge_result = await exercise.judge.judge()
            judgment = Judgment.PASS if judge_result else Judgment.FAIL
            logging.info(f'{exercise.tree_path} was judged {judgment}')
            exercise.judgment = judgment

        logging.info(f'Enqueueing judgment request for {exercise.tree_path}')
        exercise.judgment = Judgment.UNKNOWN
        self.__event_loop.call_soon_threadsafe(lambda: self.__event_loop.create_task(perform_judging()))

    def judge_recursively(self, content_node: ContentNode, only_unknown=False) -> None:
        for exercise in content_node.exercises:
            if not only_unknown or exercise.judgment is Judgment.UNKNOWN:
                self.judge(exercise)

    def write_cache(self, root: ContentNode) -> None:
        cache = {}
        for exercise in root.exercises:
            if exercise.judgment != Judgment.UNKNOWN:
                cache[str(exercise.tree_path)] = str(exercise.judgment)
        with settings.judgment_cache().open('w') as file:
            json.dump(cache, file)
