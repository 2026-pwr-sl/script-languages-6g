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
    subnet_mask_length,
    is_ip_in_subnet,
    requests_from_subnet,
    print_requests_from_subnet,
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