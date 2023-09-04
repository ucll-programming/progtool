import abc
import logging
from pathlib import Path
from typing import Callable, Optional

import flask

from progtool.content.tree import ContentNode


class Protocol(abc.ABC):
    @abc.abstractmethod
    def serve(self, content_node: ContentNode, filename: str) -> flask.Response:
        ...


class LambdaProtocol(Protocol):
    __callable: Callable[[ContentNode, str], flask.Response]

    def __init__(self, callable: Callable[[ContentNode, str], flask.Response]):
        self.__callable = callable

    def serve(self, content_node: ContentNode, filename: str) -> flask.Response:
        return self.__callable(content_node, filename)


def protocol(extension: str):
    def wrapper(function: Callable[[ContentNode, str], flask.Response]) -> Callable[[ContentNode, str], flask.Response]:
        _protocols[extension] = LambdaProtocol(function)
        return function

    return wrapper


_protocols: dict[str, Protocol] = {}


def find_protocol(extension: str) -> Optional[Protocol]:
    return _protocols.get(extension, None)


@protocol('png')
def serve_png(content_node: ContentNode, filename: str) -> flask.Response:
    return serve_binary_file(content_node.local_path / filename, 'image/png')


@protocol('jpg')
def serve_jpg(content_node: ContentNode, filename: str) -> flask.Response:
    return serve_binary_file(content_node.local_path / filename, 'image/jpeg')


@protocol('jpeg')
def serve_jpeg(content_node: ContentNode, filename: str) -> flask.Response:
    return serve_binary_file(content_node.local_path / filename, 'image/jpeg')


@protocol('svg')
def serve_svg(content_node: ContentNode, filename: str) -> flask.Response:
    return serve_text_file(content_node.local_path / filename, 'image/svg+xml')


def serve_text_file(path: Path, mimetype: str) -> flask.Response:
    logging.info(f"Serving file {path}")
    if not path.is_file():
        return flask.Response(f"File {path} not found", status=404)
    data = path.read_text(encoding='utf-8')
    return flask.Response(data, mimetype=mimetype)


def serve_binary_file(path: Path, mimetype: str) -> flask.Response:
    logging.info(f"Serving file {path}")
    if not path.is_file():
        return flask.Response(f"File {path} not found", status=404)
    data = path.read_bytes()
    return flask.Response(data, mimetype=mimetype)
