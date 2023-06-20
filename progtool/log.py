from rich.logging import RichHandler
import logging


def _logger():
    return logging.getLogger('rich')


def configure(verbosity_level: int) -> None:
    match verbosity_level:
        case 1:
            level = logging.INFO
        case 2:
            level = logging.DEBUG

    logging.basicConfig(
        handlers=[RichHandler()],
        level=level,
        force=True,
    )


def info(*args) -> None:
    _logger().info(*args)


def warning(*args) -> None:
    _logger().warning(*args)


def error(*args) -> None:
    _logger().error(*args)


def debug(*args) -> None:
    _logger().debug(*args)


def critical(*args) -> None:
    _logger().critical(*args)
