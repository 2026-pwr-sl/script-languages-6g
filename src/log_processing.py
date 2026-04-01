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
        if 400<=status<600:
            print("!" + path)
        else:
            print(path)


# Main execution pipe
lines = sys.stdin.readlines()
data = read_log(lines)
display_log(data)