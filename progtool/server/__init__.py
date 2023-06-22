from progtool.material.tree import MaterialTreeBranch, create_material_tree, MaterialTreeNode, Section, Exercise, Explanation
from progtool.server.pods import ExerciseData, ExplanationData, NodeData, SectionData, judgement_to_string
from typing import Any, Optional
from progtool import repository
import flask
import logging
import pkg_resources
import sass
import asyncio
import threading


app = flask.Flask(__name__)

material_tree = create_material_tree(repository.find_exercises_root())


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

    thread = threading.Thread(target=thread_proc, daemon=True)
    thread.start()

    event.wait()
    assert event_loop is not None, 'BUG: event loop should have been created by thread'

    return event_loop


@app.route('/', defaults={'node_path': ''})
@app.route('/nodes/<path:node_path>')
def root(node_path: str):
    html_path = 'G:/repos/ucll/programming/frontend/dist/index.html'
    with open(html_path, encoding='utf-8') as file:
        contents = file.read()
    return contents


@app.route('/api/v1/nodes/', defaults={'node_path': ''})
@app.route('/api/v1/nodes/<path:node_path>')
def node_page(node_path: str):
    path_parts = node_path.split('/') if node_path else []
    current = material_tree
    # TODO Error checking
    for path_part in path_parts:
        assert isinstance(current, MaterialTreeBranch) # TODO Raise exception
        current = current[path_part]

    path = str(current.path)
    tree_path = current.tree_path.parts
    name = current.name

    match current:
        case Section(children=children):
            data: NodeData = SectionData(
                path=path,
                type='section',
                tree_path=tree_path,
                name=name,
                children=[child.tree_path.parts[-1] for child in children]
            )
        case Explanation(markdown=markdown):
            data = ExplanationData(
                path=path,
                type='explanation',
                tree_path=tree_path,
                name=name,
                markdown=markdown
            )
        case Exercise(markdown=markdown, judgement=judgement, difficulty=difficulty):
            data = ExerciseData(
                path=path,
                type='exercise',
                tree_path=tree_path,
                name=name,
                markdown=markdown,
                difficulty=difficulty,
                judgement=judgement_to_string(judgement)
            )
        case _:
            raise RuntimeError(f"Unrecognized node type: {current!r}")

    return flask.jsonify(data.dict())


@app.route('/styles.css')
def stylesheet():
    scss = pkg_resources.resource_string('progtool.styles', 'styles.scss')
    css = sass.compile(string=scss)
    return flask.Response(css, mimetype='text/css')


def run():
    logging.info('Setting up server...')

    logging.info('Setting up background thread')
    event_loop = start_event_loop_in_separate_thread()

    logging.info('Judging exercises in background')
    event_loop.call_soon_threadsafe(lambda: material_tree.judge_recursively(event_loop))

    # TODO Turn off debug mode
    logging.info('Starting up Flask')
    app.run(debug=True)
