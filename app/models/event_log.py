import logging
import os
import threading

from utils.process import ThreadWithReturnValue

DEFAULT_FIND_EVENT_NUM = 10
DEFAULT_FIND_TIMEOUT = 5 * 60
DEFAULT_BUFFER_SIZE = 16


logger = logging.getLogger(__name__)


class EventLogFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.file_descriptor = os.open(self.filename, os.O_RDONLY)
        self.file_stat = os.fstat(self.file_descriptor)
        self._offset = self.file_stat.st_size
        self._current_pos = self._offset
        self._match_line = []
        self._lock = threading.Lock()

    def __del__(self):
        os.close(self.file_descriptor)

    def add_match_line(self, line: str) -> None:
        with self._lock:
            self._match_line.append(line)

    def clear_match_line(self) -> None:
        with self._lock:
            self._match_line = []

    def move_pos(self, pos):
        os.lseek(self.file_descriptor, pos, os.SEEK_SET)

    def get_char(self, length=1):
        c = os.read(self.file_descriptor, length)
        return c.decode()

    def add_match_line(self, line: str) -> None:
        with self._lock:
            self._match_line.append(line)

    @property
    def is_begin(self):
        return self._offset <= 0

    def move_pos(self, num=-1):
        self._offset += num
        os.lseek(self.file_descriptor, self._offset, os.SEEK_SET)

    def search(self, keywords: list, limit: int = DEFAULT_FIND_EVENT_NUM) -> list:
        if type(keywords) is not list:
            raise ValueError

        match_count = 0
        match = False
        line = ""
        # TODO (sakaijunsoccer) Create AND/OR with text/keyword
        keyword = keywords[0]
        reverted_keyword = keyword[::-1]
        len_keyword = len(keyword)

        while len(self._match_line) < limit:
            if self.is_begin:
                if match:
                    self.add_match_line(line)
                break

            self.move_pos(-1)

            c = self.get_char(1)
            if c == os.linesep:
                if match:
                    self.add_match_line(line)
                match, line = False, ""
                continue

            line = c + line
            if match_count < len_keyword and c == reverted_keyword[match_count]:
                match_count += 1
                if match_count == len_keyword:
                    match = True
            else:
                match_count = 0
        return self._match_line

    def find_event(
        self,
        keywords: list,
        limit: int = DEFAULT_FIND_EVENT_NUM,
        timeout: int = DEFAULT_FIND_TIMEOUT,
    ) -> (list, bool):

        self.clear_match_line()
        is_timeout = False

        # TODO (sakaijunsoccer) Replace professional asyc service such as SQS or celery
        thread_with_return_value = ThreadWithReturnValue(target=self.search, args=(keywords, limit,))
        thread_with_return_value.start()
        result = thread_with_return_value.join(timeout=timeout)
        if result is None:
            is_timeout = True
            current_match_line = self._match_line
            self.clear_match_line()
            return current_match_line, is_timeout
        return result, is_timeout


class EventLogFileBuffer(object):
    def __init__(self, filename, buffer_size=DEFAULT_BUFFER_SIZE):
        self.filename = filename
        self.file_descriptor = os.open(self.filename, os.O_RDONLY)
        self.file_stat = os.fstat(self.file_descriptor)
        self._offset = self.file_stat.st_size
        self._current_pos = self._offset
        self._buffer = ""
        self._buffer_size = buffer_size
        self._match_line = []
        self._lock = threading.Lock()
        self.read_buffer()

    def __del__(self):
        os.close(self.file_descriptor)

    def add_match_line(self, line: str) -> None:
        with self._lock:
            self._match_line.append(line)

    def clear_match_line(self) -> None:
        with self._lock:
            self._match_line = []

    def read_buffer(self):
        if self._offset < self._buffer_size:
            n = self._offset
        else:
            n = self._buffer_size

        if n == 0:
            return False

        self._offset -= n
        os.lseek(self.file_descriptor, self._offset, os.SEEK_SET)
        binary_buffer = os.read(self.file_descriptor, n)
        self._buffer = binary_buffer.decode() + self._buffer
        return self._buffer

    @property
    def pos(self):
        return self._current_pos - self._offset

    def move_pos(self, n):
        self._current_pos -= n

    def get_char(self):
        return self._buffer[self.pos]

    def trim(self):
        self._buffer = self._buffer[: self.pos + 1]

    def find_line_break_or_end(self):
        while self.get_char() != os.linesep:
            if self.pos == 0:
                if self._offset == 0:
                    return False
                self.read_buffer()
            self.move_pos(1)
        return True

    def search(self, keywords, limit=DEFAULT_FIND_EVENT_NUM):
        if type(keywords) is not list:
            raise ValueError
        # TODO (sakaijunsoccer) Implementing AND OR for multiple searches
        keyword = keywords[0]
        len_keyword = len(keyword)
        last_char_for_keyword = keyword[-1]
        self.clear_match_line()
        while len(self._match_line) < limit:
            if self.pos < len_keyword:
                if not self.read_buffer():
                    return self._match_line

            found = False
            while self.pos > 0:
                self.move_pos(1)
                c = self.get_char()
                if c == os.linesep:
                    self.trim()
                elif c == last_char_for_keyword:
                    found = True
                    break

                if self.pos == 0:
                    if self._offset == 0:
                        return self._match_line
                    self.read_buffer()

            if self.pos < len_keyword:
                self.read_buffer()

            if found:
                pos_plus_keyword = self.pos - (len_keyword - 1)
                if (
                    self._buffer.find(
                        keyword, pos_plus_keyword, pos_plus_keyword + len_keyword
                    )
                    == pos_plus_keyword
                ):
                    self.move_pos(len_keyword - 1)

                    if self.find_line_break_or_end():
                        line = self._buffer[self.pos + 1 :]
                    else:
                        line = self._buffer[self.pos :]

                    if line[-1] == os.linesep:
                        line = line[:-1]

                    self.add_match_line(line)
                    self.trim()
                else:
                    self.move_pos(1)
        return self._match_line

    def find_event(
        self,
        keywords: list,
        limit: int = DEFAULT_FIND_EVENT_NUM,
        timeout: int = DEFAULT_FIND_TIMEOUT,
    ) -> (list, bool):
        # TODO (sakaijunsoccer) Replace professional asyc service such as SQS or celery
        self.clear_match_line()
        is_timeout = False
        thread_with_return_value = ThreadWithReturnValue(
            target=self.search, args=(keywords, limit,)
        )
        thread_with_return_value.start()
        result = thread_with_return_value.join(timeout=timeout)
        if result is None:
            is_timeout = True
            current_match_line = self._match_line
            self.clear_match_line()
            return current_match_line, is_timeout
        return self._match_line, is_timeout
