from progtool.judging.judge import Judge
from pathlib import Path
import logging
import asyncio
import os


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

            command = f'pytest {filename}'
            process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, cwd=parent_directory)
            stdout, stderr = await process.communicate() # TODO Would process.wait() work?
            output = stdout.decode()
            tests_passed = process.returncode == 0
            return tests_passed
        except Exception as e:
            logging.error(f"Error occurred while judging {self.__tests_path}: {e}")
            return False
