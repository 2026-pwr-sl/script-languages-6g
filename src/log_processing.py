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

import logging
import sys


# Parse lines into list of (path, status, bytes_sent, processing_time)
def read_log(lines):
    logging.debug("Read %d raw lines from stdin", len(lines))

    result = []
    for line in lines:
        field = line.strip().split()
        if len(field) == 4:  # log entry must have 4 fields to be parsed
            entry = (
                field[0],
                int(field[1]),
                int(field[2]),
                int(field[3])
            )
            result.append(entry)
            logging.debug("Parsed line: %s", entry)
        else:
            logging.debug("Skipped line: %s", line.strip())

    logging.debug("Parsed %d log entries", len(result))
    return result


# Print paths from log entries, prefixing failed reads with !
def display_log(data):
    logging.debug("Displaying %d log entries", len(data))

    for path, status, _, _ in data:
        if 400 <= status < 600:
            print("!" + path)
        else:
            print(path)


def count_failed_requests(data):
    failed_requests = 0

    for _, status, _, _ in data:
        if 400 <= status < 600:
            failed_requests += 1
            logging.debug(
                "Counted failed request, status=%d current_total=%d",
                status,
                failed_requests,
            )

    logging.debug("Final failed requests count: %d", failed_requests)
    return failed_requests


def calculate_total_bytes_sent(data):
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
    total_kilobytes = total_bytes / 1024
    logging.debug(
        "Converted bytes to kilobytes, bytes=%d kilobytes=%.2f",
        total_bytes,
        total_kilobytes,
    )
    return total_kilobytes


def calculate_average_processing_time(data):
    if not data:
        logging.debug(
            "Average processing time requested for empty data set"
        )
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


def display_statistics(data):
    failed_requests = count_failed_requests(data)
    total_bytes = calculate_total_bytes_sent(data)
    total_kilobytes = convert_bytes_to_kilobytes(total_bytes)
    average_processing_time = calculate_average_processing_time(data)

    print(f"Failed requests: {failed_requests}")
    print(f"Total bytes sent: {total_bytes}")
    print(f"Total kilobytes sent: {total_kilobytes:.2f}")
    print(
        "Average processing time: "
        f"{average_processing_time:.2f} ms"
    )


def main():
    lines = sys.stdin.readlines()
    data = read_log(lines)
    display_log(data)
    display_statistics(data)


if __name__ == "__main__":
    main()
