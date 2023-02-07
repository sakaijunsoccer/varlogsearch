import logging
import os
import threading
from typing import Union

from utils.process import ThreadWithReturnValue

DEFAULT_FIND_EVENT_NUM = 10
DEFAULT_FIND_TIMEOUT = 5 * 60
DEFAULT_BUFFER_SIZE = 16


logger = logging.getLogger(__name__)


class EventRunThread(object):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._match_line = []

    def add_match_line(self, line: str) -> None:
        with self._lock:
            self._match_line.append(line)

    def clear_match_line(self) -> None:
        with self._lock:
            self._match_line = []

    @property
    def match_line(self) -> None:
        with self._lock:
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
            target=self.search,
            args=(
                keywords,
                limit,
            ),
        )
        thread_with_return_value.start()
        result = thread_with_return_value.join(timeout=timeout)
        if result is None:
            is_timeout = True
            cursor_match_line = self._match_line
            self.clear_match_line()
            return cursor_match_line, is_timeout
        return self._match_line, is_timeout


class EventLogFile(EventRunThread):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.file_descriptor = os.open(self.filename, os.O_RDONLY)
        self.file_stat = os.fstat(self.file_descriptor)
        self._offset = self.file_stat.st_size
        self._cursor = self._offset

    def __del__(self) -> None:
        os.close(self.file_descriptor)

    def move_cursor(self, pos: int) -> None:
        os.lseek(self.file_descriptor, pos, os.SEEK_SET)

    def get_char(self, length: int = 1) -> str:
        c = os.read(self.file_descriptor, length)
        return c.decode()

    @property
    def is_begin(self) -> bool:
        return self._offset <= 0

    def move_cursor(self, num: int = -1) -> None:
        self._offset += num
        os.lseek(self.file_descriptor, self._offset, os.SEEK_SET)

    def search(self, keywords: list, limit: int = DEFAULT_FIND_EVENT_NUM) -> list:
        if type(keywords) is not list:
            raise ValueError

        # TODO (sakaijunsoccer) Implement AND search
        keyword = keywords[0].strip()
        if not keyword:
            raise ValueError

        match_count, match, line = 0, False, ""
        match = False
        line = ""

        reverted_keyword = keyword[::-1]
        len_keyword = len(reverted_keyword)

        while len(self.match_line) < limit:
            if self.is_begin:
                if match:
                    self.add_match_line(line)
                break

            self.move_cursor(-1)

            c = self.get_char(1)
            if c == os.linesep:
                if match:
                    self.add_match_line(line)
                match, line = False, ""
                continue

            line = c + line
            if c == reverted_keyword[match_count]:
                match_count += 1
                if match_count == len_keyword:
                    match = True
                    match_count = 0
            else:
                match_count = 0
        return self.match_line


class EventLogFileBuffer(EventRunThread):
    def __init__(self, filename: str, buffer_size: int = DEFAULT_BUFFER_SIZE) -> None:
        super().__init__()
        self.filename = filename
        self.file_descriptor = os.open(self.filename, os.O_RDONLY)
        self.file_stat = os.fstat(self.file_descriptor)
        self._offset = self.file_stat.st_size
        self._cursor = self._offset

        self._buffer = ""
        self._buffer_size = buffer_size
        self.read_buffer()

    def __del__(self) -> None:
        os.close(self.file_descriptor)

    def read_buffer(self) -> Union[str, bool]:
        if self._offset < self._buffer_size:
            num = self._offset
        else:
            num = self._buffer_size

        if num == 0:
            return False

        self._offset -= num
        os.lseek(self.file_descriptor, self._offset, os.SEEK_SET)
        binary_buffer = os.read(self.file_descriptor, num)
        self._buffer = binary_buffer.decode() + self._buffer
        return self._buffer

    @property
    def pos(self) -> int:
        return self._cursor - self._offset

    def move_cursor(self, num: int = -1) -> None:
        self._cursor += num

    def get_char(self) -> str:
        return self._buffer[self.pos]

    def trim(self) -> None:
        self._buffer = self._buffer[: self.pos + 1]

    def find_and_move_line_break_or_start(self) -> bool:
        while self.get_char() != os.linesep:
            if self.pos == 0:
                if self._offset == 0:
                    return False
                self.read_buffer()
            self.move_cursor(-1)
        return True

    def search(self, keywords: list, limit=DEFAULT_FIND_EVENT_NUM) -> list:
        if type(keywords) is not list:
            raise ValueError

        # TODO (sakaijunsoccer) Implement AND search
        keyword = keywords[0].strip()
        if not keyword:
            raise ValueError

        len_keyword = len(keyword)
        last_char_of_keyword = keyword[-1]
        while len(self.match_line) < limit:
            if self.pos < len_keyword:
                if not self.read_buffer():
                    return self.match_line

            is_match_last_keyword_char = False
            while self.pos > 0:
                self.move_cursor(-1)
                c = self.get_char()
                if c == os.linesep:
                    self.trim()
                elif c == last_char_of_keyword:
                    is_match_last_keyword_char = True
                    break

                if self.pos == 0:
                    if self._offset == 0:
                        return self.match_line
                    self.read_buffer()

            if self.pos < len_keyword:
                self.read_buffer()

            if is_match_last_keyword_char:
                back_len_keyword = self.pos - (len_keyword - 1)
                is_match_word = self._buffer.find(
                    keyword, back_len_keyword, back_len_keyword + len_keyword) == back_len_keyword
                if is_match_word:
                    self.move_cursor(-(len_keyword - 1))

                    if self.find_and_move_line_break_or_start():
                        line = self._buffer[self.pos + 1 :]
                    else:
                        line = self._buffer[:]

                    if line[-1] == os.linesep:
                        line = line[:-1]

                    self.add_match_line(line)
                    self.trim()
                else:
                    self.move_cursor(-1)
        return self.match_line
