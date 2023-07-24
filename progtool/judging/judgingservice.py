import asyncio
import logging
from typing import Optional
from progtool.content.tree import ContentNode, Exercise
import threading
import json

from progtool.judging.judgment import Judgment
from progtool import settings


class JudgingService:
    __event_loop: asyncio.AbstractEventLoop

    def __init__(self):
        self.__event_loop = self.__start_event_loop_in_separate_thread()

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

    def judge_recursively(self, content_node: ContentNode) -> None:
        for exercise in content_node.exercises:
            self.judge(exercise)

    def initialize(self, root: ContentNode) -> None:
        logging.info('Reading cache')
        cache_path = settings.judgment_cache()
        if cache_path.is_file():
            with cache_path.open() as file:
                cache: dict[str, str] = json.load(file)
        else:
            logging.info('No cache found')
            cache = {}

        logging.info('Initializing exercise judgments')
        for exercise in root.exercises:
            path = str(exercise.tree_path)
            if path in cache:
                exercise.judgment = Judgment[cache[path]]
            else:
                self.judge(exercise)

    def write_cache(self, root: ContentNode) -> None:
        cache = {}
        for exercise in root.exercises:
            if exercise.judgment != Judgment.UNKNOWN:
                cache[str(exercise.tree_path)] = str(exercise.judgment)
        with settings.judgment_cache().open('w') as file:
            json.dump(cache, file)

    def __start_event_loop_in_separate_thread(self) -> asyncio.AbstractEventLoop:
        def thread_proc():
            nonlocal event_loop
            logging.info('Background thread reporting for duty')
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)

            event.set()

            try:
                logging.info('Background thread getting ready to process tasks')
                event_loop.run_forever()
            finally:
                event_loop.close()

        event_loop: Optional[asyncio.AbstractEventLoop] = None
        event = threading.Event()

        thread = threading.Thread(target=thread_proc, daemon=True, name="BGThread")
        thread.start()

        event.wait()
        assert event_loop is not None, 'BUG: event loop should have been created by background thread'

        return event_loop
