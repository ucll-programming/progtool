from typing import Optional
from rich.logging import RichHandler
import logging



def configure(verbosity_level: Optional[int]) -> None:
    match verbosity_level:
        case None:
            level = logging.ERROR
        case 1:
            level = logging.INFO
        case 2:
            level = logging.DEBUG

    logging.basicConfig(
        handlers=[RichHandler()],
        level=level,
        force=True,
    )
