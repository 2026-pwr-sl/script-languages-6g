import os
import sys
import unittest
from datetime import datetime, timezone
from ipaddress import IPv4Address

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from lab5 import LogEntry, parse_timestamp, parse_line_to_logentry, read_log, ip_find,  longest_request


class TestLogProcessing(unittest.TestCase):
    def test_parse_timestamp_returns_datetime(self):
        result = parse_timestamp("[03/Jan/2026:02:14:55 +0100]")
        expected = datetime(2026, 1, 3, 1, 14, 55, tzinfo=timezone.utc)
        self.assertEqual(result, expected.astimezone(result.tzinfo))

    def test_parse_line_to_logentry_returns_log_entry_object(self):
        line = '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823'
        entry = parse_line_to_logentry(line)

        self.assertIsInstance(entry, LogEntry)
        self.assertEqual(entry.ip, IPv4Address("185.23.54.12"))
        self.assertEqual(entry.path, "/home")
        self.assertEqual(entry.status, 200)
        self.assertEqual(entry.bytes_sent, 1823)

    def test_read_log_returns_list_of_objects(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "POST /api/login HTTP/1.1" 401 642\n',
            '\n',
        ]

        result = read_log(lines)

        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(entry, LogEntry) for entry in result))
        self.assertEqual(result[0].path, "/home")
        self.assertEqual(result[1].status, 401)

    def test_ip_find_returns_most_active_ips(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823\n',
            '185.23.54.12 - - [03/Jan/2026:02:15:55 +0100] "GET /about HTTP/1.1" 200 1000\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "POST /api/login HTTP/1.1" 401 642\n',
        ]

        data = read_log(lines)
        result = ip_find(data)

        self.assertEqual(result, [IPv4Address("185.23.54.12")])

    def test_ip_find_returns_least_active_ips(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823\n',
            '185.23.54.12 - - [03/Jan/2026:02:15:55 +0100] "GET /about HTTP/1.1" 200 1000\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "POST /api/login HTTP/1.1" 401 642\n',
        ]

        data = read_log(lines)
        result = ip_find(data, most_active=False)

        self.assertEqual(result, [IPv4Address("77.91.204.33")])

    def test_ip_find_returns_many_ips_when_tied(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "POST /api/login HTTP/1.1" 401 642\n',
        ]

        data = read_log(lines)
        result = ip_find(data)

        self.assertEqual(
            result,
            [IPv4Address("185.23.54.12"), IPv4Address("77.91.204.33")]
        )

    def test_ip_find_returns_empty_list_for_empty_data(self):
        result = ip_find([])

        self.assertEqual(result, [])

    def test_longest_request_returns_request_string_and_ip(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "POST /api/very/long/login/path HTTP/1.1" 401 642\n',
            '91.12.33.44 - - [20/Mar/2026:10:20:11 +0000] "GET /about HTTP/1.1" 200 500\n',
        ]

        data = read_log(lines)
        result = longest_request(data)

        self.assertEqual(
            result,
            ("POST /api/very/long/login/path", IPv4Address("77.91.204.33"))
        )

    def test_longest_request_returns_none_for_empty_data(self):
        result = longest_request([])

        self.assertIsNone(result)

    def test_longest_request_can_return_first_when_tied(self):
        lines = [
            '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /same HTTP/1.1" 200 1823\n',
            '77.91.204.33 - - [15/Feb/2026:18:45:12 +0000] "GET /same HTTP/1.1" 200 642\n',
        ]

        data = read_log(lines)
        result = longest_request(data)

        self.assertEqual(
            result,
            ("GET /same", IPv4Address("185.23.54.12"))
        )
    

if __name__ == "__main__":
    unittest.main()
