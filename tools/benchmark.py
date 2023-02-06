import argparse
import time

from app.models.event_log import DEFAULT_BUFFER_SIZE, EventLogFile, EventLogFileBuffer

DEFAULT_FILE_LOCATION = "/var/log/random.log"


def inspect_search(filename):
    start_time = time.time()
    event_log_file = EventLogFile(filename)
    result1, is_timeout = event_log_file.find_event(["test"], limit=10000, timeout=10)
    end_time = time.time()
    assert is_timeout is False
    print(f"time: {end_time-start_time} found: {len(result1)} no buffer")

    start_time = time.time()
    event_log_file_buffer = EventLogFileBuffer(filename)
    result2, is_timeout = event_log_file_buffer.find_event(
        ["test"], limit=10000, timeout=10
    )
    end_time = time.time()
    assert is_timeout is False
    print(
        f"time: {end_time-start_time} found: {len(result2)} buffer_size={DEFAULT_BUFFER_SIZE}"
    )

    buffer_size = 4 * 1024
    start_time = time.time()
    event_log_file_buffer = EventLogFileBuffer(filename, buffer_size=4 * 1024)
    result3, is_timeout = event_log_file_buffer.find_event(
        ["test"], limit=10000, timeout=10
    )
    end_time = time.time()
    assert is_timeout is False
    print(
        f"time: {end_time-start_time}, found: {len(result3)} buffer_size={buffer_size}"
    )

    assert result1 == result2 == result3


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
