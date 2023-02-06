import argparse
import time

from app.models.event_log import EventLogFile, EventLogFileBuffer

DEFAULT_FILE_LOCATION = "/var/log/random.log"


def inspect_search(filename):
    start_time = time.time()
    event_log_file = EventLogFile(filename)
    result1, is_timeout = event_log_file.find_event(["test"], limit=10000, timeout=10)
    assert is_timeout is False
    end_time = time.time()
    print(f"time: {end_time-start_time}, found: {len(result1)}")

    start_time = time.time()
    event_log_file_buffer = EventLogFileBuffer(filename)
    result2, is_timeout = event_log_file_buffer.find_event(["test"], limit=10000, timeout=10)
    assert is_timeout is False
    end_time = time.time()
    print(f"time: {end_time-start_time}, found: {len(result2)}")

    assert result1 == result2

    start_time = time.time()
    event_log_file_buffer = EventLogFileBuffer(filename, buffer_size=4*1024)
    result3, is_timeout = event_log_file_buffer.find_event(["test"], limit=10000, timeout=10)
    assert is_timeout is False
    end_time = time.time()
    print(f"time: {end_time-start_time}, found: {len(result3)}")

    assert result1 == result3


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="inspect search time")
    parser.add_argument(
        "--filename",
        type=str,
        default=DEFAULT_FILE_LOCATION,
        help="an string for generating file location",
    )
    args = parser.parse_args()
    inspect_search(args.filename)
