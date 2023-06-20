import progtool.server


def _run_server(args):
    progtool.server.run()


def add_command_line_parser(subparser) -> None:
    parser = subparser.add_parser('server', help='Run server locally')
    parser.set_defaults(func=_run_server)
