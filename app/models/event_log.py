import logging
import os

DEFAULT_FIND_EVENT_NUM = 10


logger = logging.getLogger(__name__)


class EventLogFile(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

    def find_event(self, keywords: list, limit: int = DEFAULT_FIND_EVENT_NUM) -> list:
        return self.find_event_from_end(keywords, limit)

    def go_to_end(self, file):
        try:
            file.seek(-1, os.SEEK_END)
            file.seek(2, os.SEEK_CUR)
        except OSError:
            return False
        return True

    def go_back_one_charactor(self, file, back=-2):
        try:
            file.seek(back, os.SEEK_CUR)
        except OSError:
            return False
        return True

    def is_break_line(self, character):
        return character == b"\n"

    def find_event_from_end(self, keywords: list, limit: int) -> list:
        match_line = []
        match_count = 0
        match = False
        line = ""
        reverted_keywords = [k[::-1] for k in keywords]
        # TODO (sakaijunsoccer) Create AND/OR with text/keyword
        reverted_keyword = reverted_keywords[0]
        len_keyword = len(reverted_keyword)

        with open(self.filepath, "rb") as file:
            if not self.go_to_end(file):
                return match_line
            # TODO (sakaijunsocccer) Add timeout
            while True:
                if not self.go_back_one_charactor(file):
                    if match:
                        match_line.append(line)
                    return match_line

                character = file.read(1)
                if self.is_break_line(character):
                    # TODO (sakaijunsocccer) Regex retrieved date time
                    if match:
                        match_line.append(line)
                        match = False
                    if len(match_line) >= limit:
                        break
                    line = ""
                    continue

                try:
                    decoded_character = character.decode()
                except UnicodeDecodeError as ex:
                    logger.error({"ex": ex})
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

        return match_line
