import flask
import logging
from progtool import repository
from progtool.material.tree import create_material_tree


app = flask.Flask(__name__)

material = create_material_tree(repository.find_exercises_root())


@app.route('/')
def root():
    html_path = 'G:/repos/ucll/programming/frontend/dist/index.html'
    with open(html_path) as file:
        contents = file.read()
    return contents


@app.route('/api/v1/nodes/<path:node_path>')
def exercise_page(node_path: str):
    path_parts = node_path.split('/')
    current = material
    # TODO Error checking
    for path_part in path_parts:
        current = current[path_part]
    return current.json()


def run():
    logging.info('Setting up server...')
    global app
    # TODO Turn off debug mode
    app.run(debug=True)
