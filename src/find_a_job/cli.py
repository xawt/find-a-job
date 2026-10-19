"""Command-line interface: parses arguments, calls the other modules and prints results."""

import argparse
import sys
from importlib.metadata import version

from find_a_job.errors import EXIT_USAGE, FindAJobError


def main(argv: list[str] | None = None) -> None:
    """Run the `find-a-job` command and exit with the command's exit code.

    `argv` defaults to `sys.argv[1:]`. Without a command, prints the help and exits with 2.
    A `FindAJobError` is printed as `find-a-job: error: ...` and exits with its `exit_code`;
    any other exception is a bug and propagates with its traceback.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help(sys.stderr)
        sys.exit(EXIT_USAGE)
    try:
        sys.exit(args.handler(args))
    except FindAJobError as error:
        print(f"find-a-job: error: {error}", file=sys.stderr)
        sys.exit(error.exit_code)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with one subcommand per command.

    Each subcommand stores its handler in `args.handler`.
    """
    parser = argparse.ArgumentParser(
        prog="find-a-job",
        description="MCP server that collects LinkedIn job offers through Apify.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {version('find-a-job')}")
    parser.add_subparsers(dest="command", metavar="<command>")
    return parser
