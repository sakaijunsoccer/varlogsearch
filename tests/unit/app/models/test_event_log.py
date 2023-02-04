import tempfile
import unittest

from app.models.event_log import EventLogFile


class TestEventLogFile(unittest.TestCase):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.tempfile.close()

    def write_data(self, data: str):
        self.tempfile.write(data.encode())
        self.tempfile.flush()
        self.tempfile.seek(0)

    def test_find_event_match_begging(self):
        self.write_data("test data\n")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual(["test data"], event_log_file.find_event("test"))

    def test_find_event_match_middle(self):
        self.write_data("some test data\n")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual(["some test data"], event_log_file.find_event("test"))

    def test_find_event_match_end(self):
        self.write_data("some test\n")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual(["some test"], event_log_file.find_event("test"))

    def test_find_event_match_with_other_word(self):
        self.write_data("abc XXXXtestXXXX abc\n")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual(["abc XXXXtestXXXX abc"], event_log_file.find_event("test"))

    def test_find_event_multi_line(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            event_log_file.find_event("test"),
        )

    def test_find_event_end_no_line_break_last(self):
        self.write_data("some test 1\nsome test 2\nsome test 3")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            event_log_file.find_event("test"),
        )

    def test_find_event_multi_line_limit(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 1
        self.assertEqual(
            [
                "some test 3",
            ],
            event_log_file.find_event("test", limit),
        )

    def test_find_event_multi_line_limit_two(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 2
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
            ],
            event_log_file.find_event("test", limit),
        )

    def test_find_event_multi_line_have_more_than_limit(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 100
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            event_log_file.find_event("test", limit),
        )

    def test_find_event_does_not_match(self):
        self.write_data("abc def hij\n")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual([], event_log_file.find_event("test"))

    def test_find_event_empty(self):
        self.write_data("")
        event_log_file = EventLogFile(self.tempfile.name)
        self.assertEqual([], event_log_file.find_event("test"))
