import os
import sys

from datetime import datetime
from ipaddress import IPv4Address

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/lab9")),
)

from lab9 import (
    LogEntry,
    parse_log_line,
    subnet_mask_length,
    is_ip_in_subnet,
    requests_from_subnet,
    print_requests_from_subnet,
    requests_from_browser,
    print_requests_from_browser,
)


def make_entry(ip_address):
    return LogEntry(
        ip_address,
        datetime(2026, 1, 1),
        "GET",
        "/home",
        "HTTP/1.1",
        200,
        100,
    )


def test_subnet_mask_length_for_student_index():
    assert subnet_mask_length(284210) == 10


def test_is_ip_in_subnet_returns_true_for_matching_ip():
    assert is_ip_in_subnet("185.23.54.12") is True


def test_is_ip_in_subnet_returns_false_for_not_matching_ip():
    assert is_ip_in_subnet("77.91.204.33") is False


def test_requests_from_subnet_returns_only_matching_entries():
    entries = [
        make_entry("185.23.54.12"),
        make_entry("77.91.204.33"),
    ]

    result = requests_from_subnet(entries)

    assert len(result) == 1
    assert result[0].ip == IPv4Address("185.23.54.12")


def test_print_requests_from_subnet_returns_number_of_matches(capsys):
    entries = [
        make_entry("185.23.54.12"),
        make_entry("77.91.204.33"),
    ]

    result = print_requests_from_subnet(
        entries,
        lines_per_page=5,
        input_func=lambda message: None,
    )

    captured = capsys.readouterr()

    assert result == 1
    assert "Requests from subnet 185.0.0.0/10: 1" in captured.out
    assert "185.23.54.12" in captured.out
    assert "77.91.204.33" not in captured.out


def test_parse_log_line_reads_user_agent():
    line = (
        '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] '
        '"GET /home HTTP/1.1" 200 1823 "-" '
        '"Mozilla/5.0 Firefox/120.0"'
    )

    entry = parse_log_line(line)

    assert entry.user_agent == "Mozilla/5.0 Firefox/120.0"


def test_parse_log_line_without_user_agent_still_works():
    line = (
        '185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] '
        '"GET /home HTTP/1.1" 200 1823'
    )

    entry = parse_log_line(line)

    assert entry.ip == IPv4Address("185.23.54.12")
    assert entry.user_agent == ""


def test_requests_from_browser_returns_only_matching_entries():
    firefox_entry = LogEntry(
        "185.23.54.12",
        datetime(2026, 1, 1),
        "GET",
        "/firefox",
        "HTTP/1.1",
        200,
        100,
        "Mozilla/5.0 Firefox/120.0",
    )

    chrome_entry = LogEntry(
        "77.91.204.33",
        datetime(2026, 1, 1),
        "GET",
        "/chrome",
        "HTTP/1.1",
        200,
        100,
        "Mozilla/5.0 Chrome/120.0",
    )

    result = requests_from_browser(
        [firefox_entry, chrome_entry],
        "Firefox",
    )

    assert result == [firefox_entry]


def test_print_requests_from_browser_prints_only_matching_entries(capsys):
    firefox_entry = LogEntry(
        "185.23.54.12",
        datetime(2026, 1, 1),
        "GET",
        "/firefox",
        "HTTP/1.1",
        200,
        100,
        "Mozilla/5.0 Firefox/120.0",
    )

    chrome_entry = LogEntry(
        "77.91.204.33",
        datetime(2026, 1, 1),
        "GET",
        "/chrome",
        "HTTP/1.1",
        200,
        100,
        "Mozilla/5.0 Chrome/120.0",
    )

    result = print_requests_from_browser(
        [firefox_entry, chrome_entry],
        "Firefox",
    )

    captured = capsys.readouterr()

    assert result == 1
    assert "Requests from browser Firefox: 1" in captured.out
    assert "185.23.54.12" in captured.out
    assert "77.91.204.33" not in captured.out