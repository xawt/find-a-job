"""Exceptions raised by find-a-job. All of them derive from `FindAJobError`."""

EXIT_ERROR = 1
EXIT_USAGE = 2


class FindAJobError(Exception):
    """Base class for errors find-a-job raises on purpose.

    Anything else reaching the CLI (Apify client, OS, Python itself) is unexpected.
    `exit_code` is the CLI exit code for this kind of error.
    """

    exit_code: int = EXIT_ERROR
