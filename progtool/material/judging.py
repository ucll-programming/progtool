from typing import cast
from progtool.material.tree import Exercise, MaterialTreeNode, Section, Judgement
from pathlib import Path
import logging
import asyncio
import os


async def run_pytest(path: Path) -> bool:
    assert os.path.isfile(path / 'tests.py'), f'expected to find tests.py in {path}'
    process = await asyncio.create_subprocess_shell('pytest', stdout=asyncio.subprocess.PIPE, cwd=path)
    stdout, stderr = await process.communicate()
    logging.debug(stdout.decode())
    tests_passed = process.returncode == 0
    return tests_passed


def judge_exercise(exercise: Exercise) -> None:
    async def judge():
        logging.info(f'Judging exercise {exercise.tree_path}')
        tests_passed = await run_pytest(exercise.path)
        judgement = Judgement.PASS if tests_passed else Judgement.FAIL
        logging.info(f'Exercise {exercise.tree_path}: {judgement}')
        exercise.judgement = judgement
    logging.info(f'Enqueueing exercise {exercise.tree_path}')
    asyncio.create_task(judge())


def judge_exercises(root: MaterialTreeNode) -> None:
    def recurse(node: MaterialTreeNode):
        match node:
            case Section(children=children):
                for child in children:
                    recurse(child)
            case Exercise():
                exercise = cast(Exercise, node)
                judge_exercise(exercise)
    recurse(root)
