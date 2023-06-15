import argparse


def _run_server():
    print('Running server...')


def add_command_line_parser(subparser) -> None:
    parser = subparser.add_parser('server', help='Run server locally')
    parser.set_defaults(func=_run_server)
