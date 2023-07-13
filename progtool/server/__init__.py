from progtool.content.metadata import load_everything, load_metadata
from progtool.content.navigator import ContentNavigator
from progtool.content.tree import ContentTreeBranch, ContentTreeLeaf, build_tree, ContentNode, Section, Exercise, Explanation
from progtool.content.treepath import TreePath
from progtool.server.restdata import ExerciseRestData, ExplanationRestData, NodeRestData, SectionRestData, judgement_to_string
from progtool.server.protocols import find_protocol
from progtool import repository
from progtool.server import rest
from typing import Optional
import flask
import logging
import pkg_resources
import sass
import asyncio
import threading
import re

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

def get_content() -> Content:
    global _content
    if _content is None:
        raise ServerError("Content not yet loaded")
    else:
        return _content


def start_event_loop_in_separate_thread() -> asyncio.AbstractEventLoop:
    def thread_proc():
        nonlocal event_loop
        logging.info('Background thread reporting for duty')
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        event.set()

        try:
            event_loop.run_forever()
        finally:
            event_loop.close()

    event_loop: Optional[asyncio.AbstractEventLoop] = None
    event = threading.Event()

    thread = threading.Thread(target=thread_proc, daemon=True, name="BGThread")
    thread.start()

    event.wait()
    assert event_loop is not None, 'BUG: event loop should have been created by thread'

    return event_loop


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


@app.route('/api/v1/judgement/', defaults={'node_path': ''})
@app.route('/api/v1/judgement/<path:node_path>')
def rest_judgement(node_path: str):
    # TODO
    return ''


@app.route('/styles.css')
def stylesheet():
    scss = pkg_resources.resource_string('progtool.styles', 'styles.scss')
    css = sass.compile(string=scss)
    return flask.Response(css, mimetype='text/css')


def serve_html() -> str:
    import os
    computer_name = os.environ['COMPUTERNAME']

    if computer_name == 'LT2180298':
        html_path = 'C:/repos/ucll/programming/frontend/dist/index.html'
    else:
        html_path = 'G:/repos/ucll/programming/frontend/dist/index.html'
    with open(html_path, encoding='utf-8') as file:
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

    logging.info('Setting up background thread')
    event_loop = start_event_loop_in_separate_thread()

    logging.info('Judging exercises in background')
    event_loop.call_soon_threadsafe(lambda: _content.root.judge_recursively(event_loop))

    # TODO Turn off debug mode
    logging.info('Starting up Flask')
    app.run(debug=True)
