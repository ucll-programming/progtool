from progtool.content.metadata import load_everything, load_metadata
from progtool.content.navigator import ContentNavigator
from progtool.content.tree import ContentTreeBranch, build_tree, ContentNode, Section, Exercise, Explanation
from progtool.content.treepath import TreePath
from progtool.server.restdata import ExerciseRestData, ExplanationRestData, NodeRestData, SectionRestData, judgement_to_string
from typing import Any, Optional
from progtool import repository
import flask
import logging
import pkg_resources
import sass
import asyncio
import threading
import graphviz

class ServerError(Exception):
    pass


class Content:
    __root: ContentNode
    __navigator: ContentNavigator

    def __init__(self, root: ContentNode, navigator: ContentNavigator):
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
    if node_path.endswith(".gv"):
        parts = node_path.split('/')
        tree_path = TreePath(*parts[:-1])
        content_node = find_node(tree_path)
        filename = parts[-1]
        return serve_graphviz(content_node, filename)
    else:
        return serve_html()


@app.route('/api/v1/nodes/', defaults={'node_path': ''})
@app.route('/api/v1/nodes/<path:node_path>')
def node_rest_data(node_path: str):
    def to_tree_path(node: Optional[ContentNode]) -> Optional[tuple[str, ...]]:
        if node:
            return node.tree_path.parts
        else:
            return None

    content = get_content()
    tree_path = TreePath.parse(node_path)
    content_node = find_node(tree_path) # TODO Catch exception

    successor_tree_path = to_tree_path(content.navigator.find_successor_leaf(content_node))
    predecessor_tree_path = to_tree_path(content.navigator.find_predecessor_leaf(content_node))
    parent_tree_path = to_tree_path(content.navigator.find_parent(content_node))

    match content_node:
        case Section(children=children):
            data: NodeRestData = SectionRestData(
                type='section',
                tree_path=tree_path.parts,
                name=content_node.name,
                children=[child.tree_path.parts[-1] for child in children],
                successor_tree_path=successor_tree_path,
                predecessor_tree_path=predecessor_tree_path,
                parent_tree_path=parent_tree_path,
            )
        case Explanation(markdown=markdown):
            data = ExplanationRestData(
                type='explanation',
                tree_path=tree_path.parts,
                name=content_node.name,
                markdown=markdown,
                successor_tree_path=successor_tree_path,
                predecessor_tree_path=predecessor_tree_path,
                parent_tree_path=parent_tree_path,
            )
        case Exercise(markdown=markdown, judgement=judgement, difficulty=difficulty):
            data = ExerciseRestData(
                type='exercise',
                tree_path=tree_path.parts,
                name=content_node.name,
                markdown=markdown,
                difficulty=difficulty,
                judgement=judgement_to_string(judgement),
                successor_tree_path=successor_tree_path,
                predecessor_tree_path=predecessor_tree_path,
                parent_tree_path=parent_tree_path,
            )
        case _:
            raise RuntimeError(f"Unrecognized node type: {content_node!r}")

    return flask.jsonify(data.dict())


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


def serve_graphviz(node: ContentNode, filename: str) -> flask.Response:
    # graphviz.Source.from_file()
    data = ""
    return flask.Response(data, mimetype="image/svg+xml")


def find_node(tree_path: TreePath) -> ContentNode:
    current = get_content().root
    logging.critical(f'tree_path={tree_path}')
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
