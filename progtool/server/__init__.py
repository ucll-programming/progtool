from typing import cast
import flask
import logging
from progtool import repository
from progtool.material.tree import create_material_tree, MaterialTreeNode, SectionNode, ExerciseLeaf, ExplanationLeaf


app = flask.Flask(__name__)

material_tree = create_material_tree(repository.find_exercises_root())


@app.route('/')
def root():
    html_path = 'G:/repos/ucll/programming/frontend/dist/index.html'
    with open(html_path) as file:
        contents = file.read()
    return contents


@app.route('/api/v1/nodes/', defaults={'node_path': ''})
@app.route('/api/v1/nodes/<path:node_path>')
def node_page(node_path: str):
    def url_for(node: MaterialTreeNode):
        return '/api/v1/nodes/' + '/'.join(node.tree_path)

    path_parts = node_path.split('/') if node_path else []
    current: MaterialTreeNode = material_tree
    # TODO Error checking
    for path_part in path_parts:
        current = current[path_part]

    data = {
        'path': str(current.path),
        'tree_path': current.tree_path,
    }
    match current.type:
        case 'section':
            section = cast(SectionNode, current)
            data['children'] = {child.name: url_for(child) for child in section.children}
        case 'explanations':
            explanations = cast(ExplanationLeaf, current)
        case 'exercise':
            exercise = cast(ExerciseLeaf, current)
    return flask.jsonify(data)


def run():
    logging.info('Setting up server...')
    global app
    # TODO Turn off debug mode
    app.run(debug=True)
