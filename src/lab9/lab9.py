"""
VARIABLES:

- lines - whole input stored as list of strings,
  so first line from file is lines[0],
  lines contain special characters like \n, \t, \r

- data - list of log_data{}  with keys:
ip, timestamp, method, path, protocol, status, bytes_sent

"""

import argparse
from datetime import datetime
import logging
import re
import sys
from ipaddress import IPv4Address, IPv4Network
import json
from pathlib import Path


CONFIG_FILE = Path(__file__).with_name("lab9.config")
CONFIG_ENCODING = "utf-8"
LOG_LINE_PATTERN = re.compile(
    r"^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+\S+\s+\S+\s+"
    r"\[(?P<timestamp>[^\]]+)\]\s+"
    r'"(?P<request_header>[^"]+)"\s+'
    r"(?P<status>\d{3})\s+"
    r"(?P<bytes_sent>\d+|-)\s*$"
)
REQUEST_HEADER_PATTERN = re.compile(
    r"^(?P<method>[A-Z]+)\s+"
    r"(?P<path>\S+)\s+"
    r"(?P<protocol>HTTP/\d(?:\.\d)?)$"
)


class LogEntry:
    def __init__(
            self,
            ip=None,
            timestamp=None,
            method=None,
            path="",
            protocol=None,
            status=0,
            bytes_sent=0,
    ):
        self.ip = IPv4Address(ip)
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.protocol = protocol
        self.status = status
        self.bytes_sent = bytes_sent

    @property
    def request_header(self):
        return f"{self.method} {self.path} {self.protocol}"

    def __str__(self):
        return (
            f"ip: {self.ip}, "
            f"time: {self.timestamp}, "
            f"request: {self.method} {self.path} {self.protocol}, "
            f"status: {self.status}, "
            f"bytes_sent: {self.bytes_sent}"
        )

    def __repr__(self):
        return (
            f"LogEntry("
            f"ip={self.ip!r}, "
            f"timestamp={self.timestamp!r}, "
            f"method={self.method!r}, "
            f"path={self.path!r}, "
            f"protocol={self.protocol!r}, "
            f"status={self.status!r}, "
            f"bytes_sent={self.bytes_sent!r}, "
            f")"
        )

    def is_success(self):
        return 200 <= self.status < 300

    def is_failed(self):
        return 400 <= self.status < 600

    def is_html(self):
        return self.path.endswith(".html")

    def bytes_in_kb(self):
        return self.bytes_sent / 1024


def parse_timestamp(ts_string):
    ts_string = ts_string.strip()
    ts_string = ts_string.strip("[]")

    date_part, time_part = ts_string.split(":")[0], ":".join(ts_string.split(":")[1:])

    day, month_str, year = date_part.split("/")
    hour, minute, second_timezone = time_part.split(":")

    second, timezone = second_timezone.split(" ")

    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    return datetime.strptime(
        f"{year}-{months[month_str]:02d}-{int(day):02d} "
        f"{int(hour):02d}:{int(minute):02d}:{int(second):02d} {timezone}",
        "%Y-%m-%d %H:%M:%S %z"
    )


def parse_log_line(line):
    """Parse one raw log line into a LogEntry object with regexes."""
    stripped_line = line.strip()

    if not stripped_line:
        return None

    log_match = LOG_LINE_PATTERN.match(stripped_line)

    if log_match is None:
        raise ValueError(f"Malformed log line: {line!r}")

    request_header = log_match.group("request_header")
    request_match = REQUEST_HEADER_PATTERN.match(request_header)

    if request_match is None:
        raise ValueError(f"Malformed HTTP request header: {request_header!r}")

    bytes_sent_text = log_match.group("bytes_sent")
    bytes_sent = 0 if bytes_sent_text == "-" else int(bytes_sent_text)

    return LogEntry(
        log_match.group("ip"),
        parse_timestamp(log_match.group("timestamp")),
        request_match.group("method"),
        request_match.group("path"),
        request_match.group("protocol"),
        int(log_match.group("status")),
        bytes_sent,
    )


def parse_line_to_logentry(line):
    """Compatibility wrapper for the single-line log parser."""
    return parse_log_line(line)


def read_log(lines):
    """Convert raw log lines into a list of LogEntry objects."""
    logging.debug("Read %d raw lines", len(lines))

    entries = []

    for line in lines:
        try:
            entry = parse_line_to_logentry(line)
        except ValueError:
            logging.warning("Skipping malformed log line: %r", line)
            continue

        if entry is not None:
            entries.append(entry)

    logging.debug("Parsed %d log entries into LogEntry objects", len(entries))
    return entries


def parse_log_lines(lines):
    """Compatibility wrapper for converting many raw log lines."""
    return read_log(lines)


def build_parser(default_log_file):
    parser = argparse.ArgumentParser(
        description="Process web server logs from standard input."
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default=default_log_file,
        help="Path to the log file (defaults to config file setting)"
    )
    parser.add_argument(
        "log_level",
        nargs="?",
        default=None,
        help="Optional log level. Use DEBUG for verbose output.",
    )
    return parser


def configure_logging(log_level):
    normalized = log_level.upper()

    if normalized == "DEBUG":
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        force=True,
    )


def display_log(data):
    """Print paths from log entries, prefixing failed reads with !."""
    logging.debug("Displaying %d log entries", len(data))

    for entry in data:
        if 400 <= entry.status < 600:
            print("!" + entry.path)
        else:
            print(entry.path)


def successful_reads(data):
    """Return entries with HTTP status 2xx."""
    success_list = []

    for entry in data:
        if 200 <= entry.status < 300:
            success_list.append(entry)

    logging.info("Number of successful entries: %d", len(success_list))
    return success_list


def failed_reads(data):
    """Return merged list of entries with HTTP status 4xx and 5xx."""
    failed_400s = []
    failed_500s = []

    for entry in data:
        if 400 <= entry.status < 500:
            failed_400s.append(entry)
        elif 500 <= entry.status < 600:
            failed_500s.append(entry)

    fail_list = failed_400s + failed_500s

    logging.info("Number of 4xx entries: %d", len(failed_400s))
    logging.info("Number of 5xx entries: %d", len(failed_500s))

    return fail_list


def count_failed_requests(data):
    """Return number of failed requests."""
    total_failed = len(failed_reads(data))
    logging.debug("Final failed requests count: %d", total_failed)
    return total_failed


def calculate_total_bytes_sent(data):
    """Return total bytes sent to the user."""
    total_bytes = 0

    for entry in data:
        total_bytes += entry.bytes_sent
        logging.debug(
            "Added bytes for %s, bytes_sent=%d current_total=%d",
            entry.path,
            entry.bytes_sent,
            total_bytes,
        )

    logging.debug("Final total bytes sent: %d", total_bytes)
    return total_bytes


def convert_bytes_to_kilobytes(total_bytes):
    """Convert bytes to kilobytes."""
    total_kilobytes = total_bytes / 1024
    logging.debug(
        "Converted bytes to kilobytes, bytes=%d kilobytes=%.2f",
        total_bytes,
        total_kilobytes,
    )
    return total_kilobytes


def find_largest_resource(data):
    """Return the entry with the highest bytes_sent value."""
    if not data:
        logging.debug("Largest resource requested for empty data set")
        return None

    largest_entry = data[0]
    logging.debug("Starting largest resource search with: %s", largest_entry)

    for entry in data[1:]:
        logging.debug(
            "Comparing current entry %s (%d bytes) with largest %s (%d bytes)",
            entry.path,
            entry.bytes_sent,
            largest_entry.path,
            largest_entry.bytes_sent,
        )

        if entry.bytes_sent > largest_entry.bytes_sent:
            largest_entry = entry
            logging.debug("New largest resource found: %s", largest_entry)

    return largest_entry


def non_existent(data):
    """Return unique request strings with HTTP status 404."""
    requests = []

    for entry in data:
        if entry.status == 404:
            request = f'{entry.method} {entry.path} {entry.protocol}'
            if request not in requests:
                requests.append(request)

    return requests


def requests_per_ip(data):
    """Return a dictionary with request counts for each IP address."""
    request_counts = {}

    for entry in data:
        ip = entry.ip
        request_counts[ip] = request_counts.get(ip, 0) + 1

    return request_counts


def ip_requests_number(data, ip_address):
    """Return number of requests made by one IP address."""
    request_counts = requests_per_ip(data)
    return request_counts.get(IPv4Address(ip_address), 0)


def ip_find(data, most_active=True):
    """Return IP addresses with the highest or lowest number of requests."""
    request_counts = requests_per_ip(data)

    if not request_counts:
        return []

    if most_active:
        searched_count = max(request_counts.values())
    else:
        searched_count = min(request_counts.values())

    result = []
    for ip_address, count in request_counts.items():
        if count == searched_count:
            result.append(ip_address)

    return result


def longest_request(data):
    """Return the longest request string together with its IP address."""
    if not data:
        return None

    longest_entry = data[0]
    longest_request_string = f'{longest_entry.method} {longest_entry.path}'

    for entry in data[1:]:
        request_string = f'{entry.method} {entry.path}'

        if len(request_string) > len(longest_request_string):
            longest_entry = entry
            longest_request_string = request_string

    return longest_request_string, longest_entry.ip


def display_statistics(data):
    """Print statistics required by the assignment."""
    largest_entry = find_largest_resource(data)
    failed_requests = count_failed_requests(data)
    total_bytes = calculate_total_bytes_sent(data)
    total_kilobytes = convert_bytes_to_kilobytes(total_bytes)

    if largest_entry is not None:
        print(
            "Largest resource: "
            f"{largest_entry.path} ({largest_entry.bytes_sent} b)"
        )

    print(f"Failed requests: {failed_requests}")
    print(f"Total bytes sent: {total_bytes}")
    print(f"Total kilobytes sent: {total_kilobytes:.2f}")


def html_entries(data):
    """Return successfully retrieved .html entries."""
    success_list = successful_reads(data)
    html_list = []

    for entry in success_list:
        if entry.path.endswith(".html"):
            html_list.append(entry)

    return html_list


def print_html_entries(data):
    """Print successfully retrieved .html entries."""
    entries = html_entries(data)
    if entries:
        print("HTML entries:")
        for entry in entries:
            print(entry)
    else:
        print("HTML entries: none")


def entries_from_network(data, network_text):
    network = IPv4Network(network_text)
    result = []

    for entry in data:
        if entry.ip in network:
            result.append(entry)

    return result


def print_requests_from_config_ip(data, ip_address):
    """Print all requests sent from the configured IP address."""
    target_ip = IPv4Address(ip_address)

    print(f"Requests from {target_ip}:")

    found = False

    for entry in data:
        if entry.ip == target_ip:
            print(entry)
            found = True

    if not found:
        print("No requests found.")


def display_requests_between(data, start_time, end_time):
    if end_time < start_time:
        print("Warning: second datetime is earlier than first.")
        return

    for entry in data:
        if start_time <= entry.timestamp <= end_time:
            print(entry)


def requests_by_method(entries, method):
    """Return all requests with the selected HTTP method."""
    selected_method = method.upper()
    return [entry for entry in entries if entry.method.upper() == selected_method]


def print_requests_with_method(entries, method, lines_per_page, input_func=input):
    """Print requests with the selected method and pause after each page."""
    if lines_per_page <= 0:
        raise ValueError("lines_per_page must be greater than zero")

    matching_entries = requests_by_method(entries, method)
    print(f"Requests with method {method.upper()}: {len(matching_entries)}")

    for index, entry in enumerate(matching_entries, start=1):
        print(entry)

        if index % lines_per_page == 0 and index < len(matching_entries):
            input_func("Press Enter to display more...")

    return len(matching_entries)


def large_responses(entries, minimum_bytes):
    """Return requests whose response size is at least minimum_bytes."""
    # This assertion helps debug incorrect configuration values.
    # A negative byte threshold would make the filtering result misleading.
    assert minimum_bytes >= 0, "minimum_bytes must not be negative"
    return [entry for entry in entries if entry.bytes_sent >= minimum_bytes]


def print_large_responses(entries, minimum_bytes):
    """Print requests controlled by custom min_bytes configuration value."""
    matching_entries = large_responses(entries, minimum_bytes)

    print(f"Requests with at least {minimum_bytes} bytes: {len(matching_entries)}")

    for entry in matching_entries:
        print(entry)

    return len(matching_entries)


def get_log_lines(filename):
    try:
        with open(filename, "r", encoding=CONFIG_ENCODING) as file:
            return file.readlines()
    except FileNotFoundError:
        logging.error("Log file '%s' does not exist.", filename)
        print(f"\nThe log file '{filename}' could not be found.")
        sys.exit(1)


def load_config_regex():
    path = CONFIG_FILE
    
    # Default values
    display_settings = {
        "lines_per_page": "10",
        "separator": " : ",
        "browser": "Chrome"
    }
    
    log_filename = "../log_timestamped.txt"
    
    logging.basicConfig(
        filename="processing_log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True
    )
    
    current_section = None

    try:
        with open(path, "r", encoding=CONFIG_ENCODING) as file:
            for line in file:
                line = line.strip()
                
                if not line:
                    continue
                    
                section_match = re.match(r"^\[(.*)\]$", line)
                if section_match:
                    current_section = section_match.group(1).strip()
                    continue
                    
                param_match = re.match(r"^([^=]+)=(.*)$", line)
                if param_match and current_section:
                    parameter = param_match.group(1).strip()
                    value = param_match.group(2).strip()
                    
                    if current_section == "Display":
                        display_settings[parameter] = value
                        
                    elif current_section == "LogFile" and parameter == "filename":
                        log_filename = value
                        
                    elif current_section == "Config":
                        if parameter == "log_level":
                            logging.getLogger().setLevel(value.upper())
                        elif parameter == "log_file":
                            handler = logging.FileHandler(value)
                            logging.getLogger().addHandler(handler)
                        elif parameter == "log_format":
                            formatter = logging.Formatter(value)
                            for h in logging.getLogger().handlers:
                                h.setFormatter(formatter)

    except FileNotFoundError:
        print(f"Configuration file '{CONFIG_FILE}' is missing.")
        sys.exit(1)

    log_filename_path = Path(log_filename)
    if not log_filename_path.is_absolute():
        log_filename = str((CONFIG_FILE.parent / log_filename_path).resolve())

    return display_settings, log_filename


def run(args=None):
    display_settings, log_filename = load_config_regex()

    parser = build_parser(default_log_file=log_filename)

    parsed_args = parser.parse_args(args)

    logging.info("Start of log processing")

    lines = get_log_lines(parsed_args.filename)
    data = read_log(lines)

#    display_log(data)
#    display_statistics(data)
#    print_html_entries(data)

#    print_requests_from_config_ip(
#        data,
#        config["ip_address"]
#    )

    logging.info("Finish of log processing")


if __name__ == "__main__":
    run()
