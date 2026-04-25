import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from lab5 import LogEntry, parse_timestamp, parse_line_to_logentry, read_log


class TestLogProcessing(unittest.TestCase):
    def test_parse_timestamp_returns_datetime(self):
        result = parse_timestamp("[03/Jan/2026:02:14:55 +0100]")
        expected = datetime(2026, 1, 3, 2, 14, 55)
        self.assertEqual(result, expected)

    def test_parse_log_line_returns_log_entry_object(self):
        line = '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823'
        entry = parse_line_to_logentry(line)

        self.assertIsInstance(entry, LogEntry)
        self.assertEqual(entry.path, "/home")
        self.assertEqual(entry.status, 200)
        self.assertEqual(entry.bytes_sent, 1823)

    def test_read_log_objects_returns_list_of_objects(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "POST /api/login HTTP/1.1" 401 642\n',
            '\n'
        ]

        result = read_log(lines)

        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(entry, LogEntry) for entry in result))
        self.assertEqual(result[0].path, "/home")
        self.assertEqual(result[1].status, 401)


if __name__ == "__main__":
    unittest.main()