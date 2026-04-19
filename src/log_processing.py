"""
VARIABLES:

- lines - whole input stored as list of strings,
  so first line from file is lines[0],
  lines contain special characters like \n, \t, \r

- data - list of tuples, each tuple represents one parsed log entry (one line)
  (path, status, bytes_sent, processing_time),
  for example line
  /index.html 200 1024 12

  is parsed into
  (/index.html, 200, 1024, 12)
"""

import argparse
from datetime import datetime
import logging
import sys


class LogEntry:
    def __init__(self, ip, timestamp, method, path, protocol, status, bytes_sent):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.protocol = protocol
        self.status = status
        self.bytes_sent = bytes_sent

    def __str__(self):
        return (
            f"{self.ip} "
            f"{self.timestamp} "
            f"{self.path} "
            f"{self.status} "
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
            f"bytes_sent={self.bytes_sent!r}"
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
    parts = ts_string.split(' ')
    parts = parts[0].split(':')
    
    hour = int(parts[1])
    minute = int(parts[2])
    second = int(parts[3])

    date_fields = parts[0].split('/')
    day = int(date_fields[0])
    month_str = date_fields[1]
    year = int(date_fields[2])

    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    return datetime(year, months[month_str], day, hour, minute, second)
   
    
def parse_line_to_logentry(line):
    parts = line.split()
    
    ip = parts[0]
    timestamp = parts[3].strip("[")
    method = parts[5].strip('"')
    path = parts[6]
    protocol = parts[7].strip('"')
    status = int(parts[8])
    bytes_sent = int(parts[9])
    
    datetime = parse_timestamp(timestamp)
    
    return LogEntry(ip, datetime, method, path, protocol, status, bytes_sent)


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


def read_log(lines):
    """Parse lines into a list of (path, status, bytes_sent, processing_time)."""
    logging.debug("Read %d raw lines from stdin", len(lines))

    result = []

    for line in lines:
        fields = line.strip().split()

        if len(fields) == 4:
            # log entry must have 4 fields to be parsed
            entry = (
                fields[0],
                int(fields[1]),
                int(fields[2]),
                int(fields[3]),
            )
            result.append(entry)
            logging.debug("Parsed line: %s", entry)
        else:
            logging.debug("Skipped line: %s", line.strip())

    logging.debug("Parsed %d log entries", len(result))
    return result


def display_log(data):
    """Print paths from log entries, prefixing failed reads with !."""
    logging.debug("Displaying %d log entries", len(data))

    for path, status, _, _ in data:
        if 400 <= status < 600:
            print("!" + path)
        else:
            print(path)


def successful_reads(data):
    """Return entries with HTTP status 2xx."""
    success_list = []

    for entry in data:
        if 200 <= entry[1] < 300:
            success_list.append(entry)

    logging.info("Number of successful entries: %d", len(success_list))
    return success_list


def failed_reads(data):
    """Return merged list of entries with HTTP status 4xx and 5xx."""
    failed_400s = []
    failed_500s = []

    for entry in data:
        if 400 <= entry[1] < 500:
            failed_400s.append(entry)
        elif 500 <= entry[1] < 600:
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

    for path, _, bytes_sent, _ in data:
        total_bytes += bytes_sent
        logging.debug(
            "Added bytes for %s, bytes_sent=%d current_total=%d",
            path,
            bytes_sent,
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


def calculate_average_processing_time(data):
    """Return average processing time in ms."""
    if not data:
        logging.debug("Average processing time requested for empty data set")
        return 0

    total_processing_time = 0

    for path, _, _, processing_time in data:
        total_processing_time += processing_time
        logging.debug(
            "Added processing time for %s, time=%d current_total=%d",
            path,
            processing_time,
            total_processing_time,
        )

    average_processing_time = total_processing_time / len(data)
    logging.debug(
        "Calculated average processing time, total=%d count=%d average=%.2f",
        total_processing_time,
        len(data),
        average_processing_time,
    )
    return average_processing_time


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
            entry[0],
            entry[2],
            largest_entry[0],
            largest_entry[2],
        )

        if entry[2] > largest_entry[2]:
            largest_entry = entry
            logging.debug("New largest resource found: %s", largest_entry)

    return largest_entry


def display_statistics(data):
    """Print statistics required by the assignment."""
    largest_entry = find_largest_resource(data)
    failed_requests = count_failed_requests(data)
    total_bytes = calculate_total_bytes_sent(data)
    total_kilobytes = convert_bytes_to_kilobytes(total_bytes)
    average_processing_time = calculate_average_processing_time(data)

    if largest_entry is not None:
        path, _, _, processing_time = largest_entry
        print(f"Largest resource: {path} ({processing_time} ms)")

    print(f"Failed requests: {failed_requests}")
    print(f"Total bytes sent: {total_bytes}")
    print(f"Total kilobytes sent: {total_kilobytes:.2f}")
    print(f"Average processing time: {average_processing_time:.2f} ms")


def html_entries(data):
    """Return successfully retrieved .html entries."""
    success_list = successful_reads(data)
    html_list = []

    for entry in success_list:
        if entry[0].endswith(".html"):
            html_list.append(entry)

    return html_list


def print_html_entries(data):
    """Print successfully retrieved .html entries."""
    entries = html_entries(data)
    print("HTML entries:")

    for entry in entries:
        print(entry)


def run(args=None):
    parser = build_parser()
    parsed_args = parser.parse_args(args)
    configure_logging(parsed_args.log_level)

    logging.info("Start of log processing")

    lines = sys.stdin.readlines()
    data = read_log(lines)

    display_log(data)
    display_statistics(data)
    print_html_entries(data)

    logging.info("Finish of log processing")


if __name__ == "__main__":
    run()