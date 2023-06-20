from progtool.material.tree import MaterialTreeBranch, create_material_tree, MaterialTreeNode, Section, Exercise, Explanation
from typing import Any
from progtool import repository
import flask
import logging
import pkg_resources
import sass

from progtool.server.pods import ExerciseData, ExplanationData, NodeData, SectionData


app = flask.Flask(__name__)

material_tree: MaterialTreeNode = create_material_tree(repository.find_exercises_root())


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
    def url_for(node: MaterialTreeNode) -> str:
        return '/api/v1/nodes/' + '/'.join(node.tree_path.parts)

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
        case Exercise(markdown=markdown):
            data = ExplanationData(
                path=path,
                type='exercise',
                tree_path=tree_path,
                name=name,
                markdown=markdown
            )

    return flask.jsonify(data.dict())


@app.route('/styles.css')
def stylesheet():
    scss = pkg_resources.resource_string('progtool.styles', 'styles.scss')
    css = sass.compile(string=scss)
    return flask.Response(css, mimetype='text/css')


def run():
    logging.info('Setting up server...')
    global app
    # TODO Turn off debug mode
    app.run(debug=True)
