import logging
import re
from typing import Literal, Optional

import flask
import pkg_resources
import pydantic
import sass

from progtool import settings
from progtool.content.tree import (ContentNode, ContentTreeBranch,
                                   ContentTreeLeaf, Exercise)
from progtool.content.treepath import TreePath
from progtool.judging.cachingservice import CachingService
from progtool.judging.judgingservice import JudgingService
from progtool.server import rest
from progtool.server.bgthread import create_background_worker
from progtool.server.content import Content, load_content
from progtool.server.error import ServerError
from progtool.server.protocols import find_protocol

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


class JudgmentSuccess(pydantic.BaseModel):
    status: Literal['ok'] = pydantic.Field(default = 'ok')
    judgments: dict[str, str]


class JudgmentFailure(pydantic.BaseModel):
    status: Literal['fail'] = pydantic.Field(default = 'fail')


@app.route('/api/v1/judgment/', defaults={'node_path': ''})
@app.route('/api/v1/judgment/<path:node_path>')
def rest_judgment(node_path: str):
    try:
        content_node = find_node(TreePath.parse(node_path))
        judgments = {}
        for exercise in content_node.exercises:
            judgments[str(exercise.tree_path)] = str(exercise.judgment).lower()
        return flask.jsonify(JudgmentSuccess(judgments=judgments).dict())
    except:
        return flask.jsonify(JudgmentFailure())


class RejudgeResponse(pydantic.BaseModel):
    status: Literal['ok'] | Literal['fail']


@app.route('/api/v1/judgment/', defaults={'node_path': ''}, methods=['POST'])
@app.route('/api/v1/judgment/<path:node_path>', methods=['POST'])
def rest_rejudge(node_path: str):
    try:
        content_node = find_node(TreePath.parse(node_path))
        get_judging_service().judge_recursively(content_node)
        response = RejudgeResponse(status='ok')
    except:
        response = RejudgeResponse(status='fail')

    return flask.jsonify(response.dict())


@app.route('/styles.css')
def stylesheet():
    scss = pkg_resources.resource_string('progtool.styles', 'styles.scss')
    css = sass.compile(string=scss)
    return flask.Response(css, mimetype='text/css')


def serve_html() -> str:
    with settings.html_path().open(encoding='utf-8') as file:
        return file.read()


def find_node(tree_path: TreePath) -> ContentNode:
    return get_content().root.descend(tree_path)


def run():
    logging.info("Loading content")
    global _content
    _content = load_content()

    logging.info('Creating background worker')
    event_loop = create_background_worker()

    logging.info('Setting up caching service')
    caching_service = CachingService(_content.root, event_loop)

    logging.info('Setting up judging service')
    global _judging_service
    _judging_service = JudgingService(event_loop)
    _judging_service.judge_recursively(_content.root, only_unknown=True)

    # TODO Turn off debug mode
    logging.info('Starting up Flask')
    app.run(debug=True)
