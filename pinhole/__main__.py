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
    appserver = subparsers.add_parser("appserver")
    collector = subparsers.add_parser("collector")
    return parser.parse_args()


def run_apiserver(args: Namespace) -> None:
    api_server_path = join(dirname(realpath(argv[0])), "servers", "apiserver", "main.py")
    argv.clear()
    argv.extend(["fastapi", "dev", api_server_path])
    environ['PINHOLE_PROJECT'] = args.project
    fastapi_main()


def run_appserver(args: Namespace) -> None:
    app_server_path = join(dirname(realpath(argv[0])), "servers", "appserver", "Pinhole.py")
    from streamlit.web.cli import main_run
    main_run([
        app_server_path,
        "--server.port", "8080",
        "--server.runOnSave", "true"
    ])


def run_collector(args: Namespace) -> None:
    from pinhole.collector import main
    main()


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
