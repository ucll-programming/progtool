import asyncio
import logging
import re
import threading
from typing import Literal, Optional

import flask
import pkg_resources
import pydantic
import sass

from progtool import repository, settings
from progtool.content.metadata import load_everything, load_metadata
from progtool.content.navigator import ContentNavigator
from progtool.content.tree import (ContentNode, ContentTreeBranch,
                                   ContentTreeLeaf, Exercise, build_tree)
from progtool.content.treepath import TreePath
from progtool.server import rest
from progtool.server.protocols import find_protocol
from progtool.judging.judgingservice import JudgingService


class ServerError(Exception):
    pass


class Content:
    __root: ContentNode
    __navigator: ContentNavigator

    def __init__(self, root: ContentNode, navigator: ContentNavigator):
        assert isinstance(root, ContentNode)
        self.__root = root
        self.__navigator = navigator

    @property
    def root(self) -> ContentNode:
        return self.__root

    @property
    def navigator(self) -> ContentNavigator:
        return self.__navigator


def load_content() -> Content:
    logging.info("Loading content...")
    root_path = repository.find_exercises_root()

    logging.info("Loading metadata")
    # TODO Add tag filtering functionality
    metadata = load_metadata(root_path, link_predicate=load_everything(force_all=True))

    if metadata is None:
        raise ServerError("No content found!")

    logging.info("Building tree")
    tree = build_tree(metadata)

    logging.info("Building navigator")
    navigator = ContentNavigator(tree)

    logging.info("Done reading content")
    return Content(tree, navigator)



app = flask.Flask(__name__)

_content: Optional[Content] = None

_judging_service: Optional[JudgingService] = None

def get_content() -> Content:
    if _content is None:
        raise ServerError("Content not yet loaded")
    else:
        return _content


def get_judging_service() -> JudgingService:
    if _judging_service is None:
        raise ServerError("Judging service is inactive")
    else:
        return _judging_service


@app.route('/')
def root():
    return serve_html()


@app.route('/nodes/<path:node_path>')
def node_page(node_path: str):
    regex = f'\.([a-zA-Z]+)$'
    if match := re.search(regex, node_path):
        extension = match.group(1)
        protocol = find_protocol(extension)
        if protocol is None:
            return flask.Response(f"Unsupported format {extension}", 400)
        parts = node_path.split('/')
        tree_path = TreePath(*parts[:-1])
        content_node = find_node(tree_path)
        filename = parts[-1]
        return protocol.serve(content_node, filename)
    else:
        return serve_html()


@app.route('/api/v1/overview')
def rest_overview():
    content = get_content()
    root = content.root
    data = rest.convert_tree(root)
    return flask.jsonify(data.dict())


@app.route('/api/v1/markdown/', defaults={'node_path': ''})
@app.route('/api/v1/markdown/<path:node_path>')
def rest_markup(node_path: str):
    content_node = find_node(TreePath.parse(node_path))
    match content_node:
        case ContentTreeLeaf(markdown=markdown):
            return flask.Response(markdown, mimetype='text/markdown')
        case _:
            return 'error', 400


class JudgementSuccess(pydantic.BaseModel):
    status: Literal['ok'] = pydantic.Field(default = 'ok')
    judgement: str


class JudgementFailure(pydantic.BaseModel):
    status: Literal['fail'] = pydantic.Field(default = 'fail')


@app.route('/api/v1/judgement/', defaults={'node_path': ''})
@app.route('/api/v1/judgement/<path:node_path>')
def rest_judgement(node_path: str):
    content_node = find_node(TreePath.parse(node_path))
    match content_node:
        case Exercise(judgment=judgement):
            success = JudgementSuccess(judgement=str(judgement).lower())
            return flask.jsonify(success.dict())
        case _:
            failure = JudgementFailure()
            return flask.Response(failure.json(), status=404)


@app.route('/styles.css')
def stylesheet():
    scss = pkg_resources.resource_string('progtool.styles', 'styles.scss')
    css = sass.compile(string=scss)
    return flask.Response(css, mimetype='text/css')


def serve_html() -> str:
    with settings.html_path().open(encoding='utf-8') as file:
        html_contents = file.read()

    return html_contents


def find_node(tree_path: TreePath) -> ContentNode:
    current = get_content().root
    for part in tree_path.parts:
        if not isinstance(current, ContentTreeBranch):
            raise ServerError("Invalid content path")
        current = current[part]
    return current


def run():
    logging.info("Loading content")
    global _content
    _content = load_content()

    logging.info('Setting up judging service')
    global _judging_service
    _judging_service = JudgingService()

    logging.info('Judging exercises in background')
    _judging_service.judge_recursively(_content.root)

    # TODO Turn off debug mode
    logging.info('Starting up Flask')
    app.run(debug=True)
