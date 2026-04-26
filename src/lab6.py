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
import sys
from ipaddress import IPv4Address,IPv4Network


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


def parse_line_to_logentry(line):
    stripped_line = line.strip()

    if not stripped_line:
        return None

    parts = stripped_line.split()

    ip_address = parts[0]
    timestamp = parse_timestamp(parts[3] + " " + parts[4])
    method = parts[5].strip('"')
    path = parts[6]
    protocol = parts[7].strip('"')
    status = int(parts[8])
    bytes_sent = int(parts[9])

    return LogEntry(ip_address, timestamp, method, path, protocol, status, bytes_sent)


def read_log(filename):
    logging.debug("Opening file: %s", filename)

    log_data = {}
    
    try:
        with open(filename, "r") as file:
            for index, line in enumerate(file):
                entry = parse_line_to_logentry(line)
                if entry:
                    log_data[index] = {
                        "ip": entry.ip,
                        "timestamp": entry.timestamp,
                        "method": entry.method,
                        "path": entry.path,
                        "protocol": entry.protocol,
                        "status": entry.status,
                        "bytes_sent": entry.bytes_sent,
                    }
    except FileNotFoundError:
        logging.error(f"File {filename} not found.")
    

    logging.debug("Parsed %d log entries into dictionary", len(log_data))
    return log_data


def build_parser():
    parser = argparse.ArgumentParser(
        description="Process web server logs from standard input."
    )
    parser.add_argument(
        "log_level",
        nargs="?",
        default="INFO",
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
        if 400 <= entry['status'] < 600:
            print("!" + entry['path'])
        else:
            print(entry['path'])


def successful_reads(data):
    """Return entries with HTTP status 2xx."""
    success_list = []

    for entry in data:
        if 200 <= entry['status'] < 300:
            success_list.append(entry)

    logging.info("Number of successful entries: %d", len(success_list))
    return success_list


def failed_reads(data):
    """Return merged list of entries with HTTP status 4xx and 5xx."""
    failed_400s = []
    failed_500s = []

    for entry in data:
        if 400 <= entry['status'] < 500:
            failed_400s.append(entry)
        elif 500 <= entry['status'] < 600:
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
        total_bytes += entry['bytes_sent']
        logging.debug(
            "Added bytes for %s, bytes_sent=%d current_total=%d",
            entry['path'],
            entry['bytes_sent'],
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
            entry['path'],
            entry['bytes_sent'],
            largest_entry['path'],
            largest_entry['bytes_sent'],
        )

        if entry['bytes_sent'] > largest_entry['bytes_sent']:
            largest_entry = entry
            logging.debug("New largest resource found: %s", largest_entry)

    return largest_entry


def non_existent(data):
    """Return unique request strings with HTTP status 404."""
    requests = []

    for entry in data:
        if entry["status"] == 404:
            request = f'{entry["method"]} {entry["path"]} {entry["protocol"]}'
            if request not in requests:
                requests.append(request)

    return requests


def requests_per_ip(data):
    """Return a dictionary with request counts for each IP address."""
    request_counts = {}

    for entry in data:
        ip = entry["ip"]
        counts[ip] = counts.get(ip, 0) + 1

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
    longest_request_string = f'{longest["method"]} {longest["path"]}'

    for entry in data[1:]:
        request_string = f'{entry["method"]} {entry["path"]}'

        if len(request_string) > len(longest_request_string):
            longest_entry = entry
            longest_request_string = request_string

    return longest_request_string, longest_entry["ip"]


def display_statistics(data):
    """Print statistics required by the assignment."""
    largest_entry = find_largest_resource(data)
    failed_requests = count_failed_requests(data)
    total_bytes = calculate_total_bytes_sent(data)
    total_kilobytes = convert_bytes_to_kilobytes(total_bytes)


    if largest_entry is not None:
        print(
            "Largest resource: "
            f"{largest_entry['path']} ({largest_entry['bytes_sent']} b)"
        )

    print(f"Failed requests: {failed_requests}")
    print(f"Total bytes sent: {total_bytes}")
    print(f"Total kilobytes sent: {total_kilobytes:.2f}")


def html_entries(data):
    """Return successfully retrieved .html entries."""
    success_list = successful_reads(data)
    html_list = []

    for entry in success_list:
        if entry['path'].endswith(".html"):
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
        if entry['ip'] in network:
            result.append(entry)

    return result


def display_requests_between(data, start_time, end_time):
    if end_time < start_time:
        print("Warning: second datetime is earlier than first.")
        return

    for entry in data:
        if start_time <= entry['timestamp'] <= end_time:
            print(entry)


def run(args=None):
    parser = build_parser()
    parser.add_argument("filename", help="Path to the log file")
    
    parsed_args = parser.parse_args(args)
    configure_logging(parsed_args.log_level)

    logging.info("Start of log processing")

    log_dict = read_log(parsed_args.filename)
    data = list(log_dict.values())

    display_log(data)
    display_statistics(data)
    print_html_entries(data)

    logging.info("Finish of log processing")


if __name__ == "__main__":
    run()
