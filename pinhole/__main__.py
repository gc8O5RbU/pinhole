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
    crawler = subparsers.add_parser("crawler")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == 'apiserver':
        api_server_path = join(dirname(realpath(argv[0])), "servers", "apiserver.py")
        argv.clear()
        argv.extend(["fastapi", "dev", api_server_path])
        environ['PINHOLE_PROJECT'] = args.project
        fastapi_main()
    else:
        print(args)


if __name__ == "__main__":
    main()
