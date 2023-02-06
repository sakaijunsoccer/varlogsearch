import tempfile
import unittest

from app.models.event_log import EventLogFile, EventLogFileBuffer


class TestEventLogFile(unittest.TestCase):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.tempfile.close()

    def write_data(self, data: str):
        self.tempfile.write(data.encode())
        self.tempfile.flush()
        self.tempfile.seek(0)

    def test_search_match_begging(self):
        self.write_data("test data\n")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["test data"], result)

    def test_search_match_middle(self):
        self.write_data("some test data\n")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["some test data"], result)

    def test_search_match_end(self):
        self.write_data("some test\n")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["some test"], result)

    def test_search_match_with_other_word(self):
        self.write_data("abc XXXXtestXXXX abc\n")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["abc XXXXtestXXXX abc"], result)

    def test_search_multi_line(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            result,
        )

    def test_search_end_no_line_break_last(self):
        self.write_data("some test 1\nsome test 2\nsome test 3")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            result,
        )

    def test_searchmulti_line_limit(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 1
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            [
                "some test 3",
            ],
            result,
        )

    def test_search_multi_line_limit_two(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 2
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
            ],
            result,
        )

    def test_search_multi_line_have_more_than_limit(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            result,
        )

    def test_search_hit_one_in_multiline(self):
        self.write_data("some test 1\nsome unique 2\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["unique"], limit)
        self.assertEqual(
            [
                "some unique 2",
            ],
            result,
        )

    def test_search_find_two_keyword_in_one_line(self):
        self.write_data("some test test 1\nsome test test 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            ["some test 3", "some test test 2", "some test test 1"],
            result,
        )

    def test_search_text_search(self):
        self.write_data("some test 1\nHello. This is text. Bye.\nsome test 3\n")
        event_log_file = EventLogFile(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["This is text"], limit)
        self.assertEqual(
            [
                "Hello. This is text. Bye.",
            ],
            result,
        )

    def test_search_find_one_char(self):
        self.write_data("some test a test\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["a"], limit)
        self.assertEqual(
            ['some test a test'],
            result,
        )

    def test_search_line_break_empty(self):
        self.write_data("some test 1\nsome test 2")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        with self.assertRaises(ValueError):
            result = event_log_file.search(["\n"], limit)

    def test_search_space_empty(self):
        self.write_data("some test 1\nsome test 2")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        with self.assertRaises(ValueError):
            result = event_log_file.search([" "], limit)

    def test_search_does_not_match(self):
        self.write_data("abc def hij\n")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual([], result)

    def test_search_empty(self):
        self.write_data("")
        event_log_file = EventLogFile(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual([], result)


class TestEventLogFileBuffer(unittest.TestCase):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.tempfile.close()

    def write_data(self, data: str):
        self.tempfile.write(data.encode())
        self.tempfile.flush()
        self.tempfile.seek(0)

    def test_search_match_begging(self):
        self.write_data("test data")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["test data"], result)

    def test_search_match_middle(self):
        self.write_data("some test data")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["some test data"], result)

    def test_search_match_end(self):
        self.write_data("some test\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["some test"], result)

    def test_search_match_with_other_word(self):
        self.write_data("abc XXXXtestXXXX abc")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(["abc XXXXtestXXXX abc"], result)

    def test_search_multi_line(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            result,
        )

    def test_search_end_no_line_break_last(self):
        self.write_data("some test 1\nsome test 2\nsome test 3")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            result,
        )

    def test_search_multi_line_limit(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 1
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            [
                "some test 3",
            ],
            result,
        )

    def test_search_multi_line_limit_two(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 2
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
            ],
            result,
        )

    def test_search_multi_line_have_more_than_limit(self):
        self.write_data("some test 1\nsome test 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            [
                "some test 3",
                "some test 2",
                "some test 1",
            ],
            result,
        )

    def test_search_hit_one_in_multiline(self):
        self.write_data("some test 1\nsome unique 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["unique"], limit)
        self.assertEqual(
            [
                "some unique 2",
            ],
            result,
        )

    def test_search_find_two_keyword_in_one_line(self):
        self.write_data("some test test 1\nsome test test 2\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["test"], limit)
        self.assertEqual(
            ["some test 3", "some test test 2", "some test test 1"],
            result,
        )

    def test_search_text_search(self):
        self.write_data("some test 1\nHello. This is text. Bye.\nsome test 3\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["This is text"], limit)
        self.assertEqual(
            [
                "Hello. This is text. Bye.",
            ],
            result,
        )

    def test_search_word_between_buffer(self):
        self.write_data("123456789\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name, buffer_size=5)
        result = event_log_file.search(["456"])
        self.assertEqual(
            [
                "123456789",
            ],
            result,
        )

    def test_search_find_one_char(self):
        self.write_data("some test a test\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        result = event_log_file.search(["a"], limit)
        self.assertEqual(
            ['some test a test'],
            result,
        )

    def test_search_line_break_empty(self):
        self.write_data("some test 1\nsome test 2")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        with self.assertRaises(ValueError):
            result = event_log_file.search(["\n"], limit)

    def test_search_space_empty(self):
        self.write_data("some test 1\nsome test 2")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        limit = 100
        with self.assertRaises(ValueError):
            result = event_log_file.search([" "], limit)

    def test_search_does_not_match(self):
        self.write_data("abc def hij\n")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual([], result)

    def test_search_empty(self):
        self.write_data("")
        event_log_file = EventLogFileBuffer(self.tempfile.name)
        result = event_log_file.search(["test"])
        self.assertEqual([], result)
