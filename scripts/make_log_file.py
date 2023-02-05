import argparse
import datetime
import os
import random
import string
from datetime import datetime

DEFAULT_LOG_LOCATION = "/tmp"
DEFAULT_LOG_FILENAME = "random.log"
DEFAULT_FILE_LOCATION = os.path.join(DEFAULT_LOG_LOCATION, DEFAULT_LOG_FILENAME)
DEFAULT_LOG_KEYWORD = "test"
DEFAULT_FILE_SIZE = 1 * 1024 * 1024 * 1024
DEFAULT_POSSIBILITY = 10


def make_random_log(
    filename: str = DEFAULT_LOG_FILENAME,
    filesize: int = DEFAULT_FILE_SIZE,
    keyword: str = DEFAULT_LOG_KEYWORD,
    occurrences: int = DEFAULT_POSSIBILITY,
    flush_size: int = 100,
) -> None:
    with open(filename, "a") as file:
        while True:
            current_file_size = os.path.getsize(filename)
            if current_file_size >= filesize:
                return True

            for i in range(flush_size):
                now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                random_string = "".join(
                    random.choice(string.ascii_lowercase + string.ascii_uppercase)
                    for i in range(random.randint(1, 10))
                )
                is_keyword = (
                    keyword if random.randint(1, occurrences) == occurrences else ""
                )
                file.write(
                    f"{now} {random_string} {is_keyword} {random_string} {os.linesep}"
                )
            file.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make random log")
    parser.add_argument(
        "--filesize",
        type=int,
        default=DEFAULT_FILE_SIZE,
        help="an integer for file size. writes a log slightly larger than the specified size",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=DEFAULT_FILE_LOCATION,
        help="an string for generating file location",
    )
    parser.add_argument(
        "--keyword", type=str, default=DEFAULT_LOG_KEYWORD, help="an string for keyword"
    )
    parser.add_argument(
        "--occurrences",
        type=int,
        default=DEFAULT_POSSIBILITY,
        help="Occurrence frequency of the word you want to insert",
    )
    args = parser.parse_args()
    make_random_log(args.filename, args.filesize, args.keyword, args.occurrences)
