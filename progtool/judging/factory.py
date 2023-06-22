from pathlib import Path
from progtool.judging.judge import Judge, JudgeError, JudgeMetadata
from progtool.judging.pytest import PytestJudge


def create_judge(path: Path, metadata: JudgeMetadata) -> Judge:
    if metadata.type == PytestJudge.ID:
        return PytestJudge(path / metadata.file)
    else:
        raise JudgeError(f'Unknown judge {metadata.type}')
