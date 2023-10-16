import asyncio
import logging
import os
from pathlib import Path

from progtool.judging.judge import Judge


class PytestJudge(Judge):
    ID = 'pytest'

    __tests_path: Path

    def __init__(self, tests_path: Path):
        self.__tests_path = tests_path

    async def judge(self) -> bool:
        try:
            tests_path = self.__tests_path
            assert os.path.isfile(tests_path), f'{tests_path} does not exist'

            parent_directory = tests_path.parent
            filename = tests_path.name

            # -x flag interrupts tests after first failure
            command = f'pytest -x {filename}'
            logging.info(f'[Pytest judge] Running {command} in {parent_directory}')
            process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, cwd=parent_directory)
            stdout, stderr = await process.communicate() # TODO Would process.wait() work?
            output = stdout.decode()
            logging.debug(f'[Pytest judge] STDOUT from pytest: {output}')
            pytest_result = process.returncode
            logging.info(f'[Pytest judge] Pytest ended with code {pytest_result} (0 indicates passed tests)')
            tests_passed = pytest_result == 0
            return tests_passed
        except Exception as e:
            logging.error(f"[Pytest judge] Error occurred while judging {self.__tests_path}: {e}")
            return False
