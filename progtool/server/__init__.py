import flask
import logging


app = flask.Flask(__name__)


@app.route('/api/v1/nodes/<path:node_path>')
def exercise_page(node_path: str):
    return node_path


def run():
    logging.info('Setting up server...')
    global app
    # TODO Turn off debug mode
    app.run(debug=True)
