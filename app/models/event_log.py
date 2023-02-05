import logging
import os
import threading

from configs import settings
from utils.process import ThreadWithReturnValue

DEFAULT_FIND_EVENT_NUM = 10

logger = logging.getLogger(__name__)


class EventLogFile(object):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.file = None
        self.lock = threading.Lock()
        self.match_line = []

    def add_match_line(self, line: list) -> None:
        with self.lock:
            self.match_line.append(line)

    def find_event(
        self,
        keywords: list,
        limit: int = DEFAULT_FIND_EVENT_NUM,
        timeout: int = settings.search_timeout,
    ) -> (list, bool):
        self.match_line = []
        is_timeout = False

        # TODO (sakaijunsoccer) Replace professional asyc service such as SQS or celery
        thread_with_return_value = ThreadWithReturnValue(
            target=self.search_char_from_back, args=(keywords, limit)
        )
        thread_with_return_value.start()
        result = thread_with_return_value.join(timeout=timeout)
        if result is None:
            is_timeout = True
            current_match_line = self.match_line
            self.match_line = []
            return current_match_line, is_timeout
        return result, is_timeout

    def go_to_end(self, file: object) -> None:
        try:
            file.seek(-1, os.SEEK_END)
            file.seek(2, os.SEEK_CUR)
        except OSError:
            return False
        return True

    def go_back_one_charactor(self, file: object, back: int = -2) -> bool:
        try:
            file.seek(back, os.SEEK_CUR)
        except OSError:
            return False
        return True

    def is_break_line(self, character: str) -> bool:
        return character == b"\n"

    def search_char_from_back(self, keywords: str, limit: int) -> list:
        match_count = 0
        match = False
        line = ""
        reverted_keywords = [k[::-1] for k in keywords]
        # TODO (sakaijunsoccer) Create AND/OR with text/keyword
        reverted_keyword = reverted_keywords[0]
        len_keyword = len(reverted_keyword)
        with open(self.filepath, "rb") as file:
            if not self.go_to_end(file):
                return self.match_line
            while True:
                if not self.go_back_one_charactor(file):
                    if match:
                        self.add_match_line(line)
                    return self.match_line

                character = file.read(1)
                if self.is_break_line(character):
                    # TODO (sakaijunsocccer) Regex retrieved date time
                    if match:
                        self.add_match_line(line)
                        match = False
                    if len(self.match_line) >= limit:
                        break
                    line = ""
                    continue

                try:
                    decoded_character = character.decode()
                except UnicodeDecodeError:
                    return False
                line = decoded_character + line
                # TODO (sakaijunsoccer) Care about upper and lower case letters if needed
                if (
                    match_count < len_keyword
                    and decoded_character == reverted_keyword[match_count]
                ):
                    match_count += 1
                    if match_count == len_keyword:
                        match = True
                else:
                    match_count = 0
        return self.match_line
