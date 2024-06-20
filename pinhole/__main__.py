from pinhole.collector import collector_add_subparser_args
from fastapi_cli.cli import main as fastapi_main

from argparse import ArgumentParser, Namespace
from os.path import realpath, join, dirname
from os import environ
from sys import argv


def parse_args() -> Namespace:
    parser = ArgumentParser("pinhole")
    subparsers = parser.add_subparsers(dest='command', required=True)
    apiserver = subparsers.add_parser("apiserver")
    apiserver.add_argument("project", type=str)
    apiserver.add_argument("--dev", action='store_true',
                           help='run as development mode in FastAPI')
    appserver = subparsers.add_parser("appserver")
    appserver.add_argument("--port", type=int, default=8080)
    collector = subparsers.add_parser("collector")
    collector_add_subparser_args(collector)
    return parser.parse_args()


def run_apiserver(args: Namespace) -> None:
    api_server_path = join(dirname(realpath(argv[0])), "servers", "apiserver", "main.py")
    argv.clear()
    argv.extend([
        "fastapi",
        "dev" if args.dev else "run",
        api_server_path
    ])
    environ['PINHOLE_PROJECT'] = args.project
    fastapi_main()


def run_appserver(args: Namespace) -> None:
    app_server_path = join(dirname(realpath(argv[0])), "servers", "appserver", "home.py")
    from streamlit.web.cli import main_run
    main_run([
        app_server_path,
        "--server.port", str(args.port),
        "--server.runOnSave", "true",
        "--client.showSidebarNavigation", "false"
    ])


def run_collector(args: Namespace) -> None:
    from pinhole.collector import main
    main(args)


def main() -> None:
    args = parse_args()
    if args.command == 'apiserver':
        run_apiserver(args)
    elif args.command == 'appserver':
        run_appserver(args)
    elif args.command == 'collector':
        run_collector(args)
    else:
        print(args)


if __name__ == "__main__":
    main()
