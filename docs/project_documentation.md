# Project Documentation

## 1. Project structure

The repository is organized into the following main directories and files:

- `src/` - application source code
- `tests/` - unit tests for project logic
- `docs/` - project documentation
- `data/` - data files
- `README.md` - general repository overview
- `requirements.txt` - Python dependencies

The main file for Lab 5 is:

- `src/lab5.py` - web server log processing module

The main test file for Lab 5 is:

- `tests/test_lab5.py` - unit tests for Lab 5 functions

---

## 2. Lab 5 overview

Lab 5 focuses on processing web server log files.

The program reads log lines, converts them into structured `LogEntry` objects, and then performs different operations on the parsed data, such as:

- displaying requested resources,
- detecting successful and failed requests,
- counting requests,
- filtering requests by IP address or network,
- calculating transferred bytes,
- finding the largest resource,
- finding HTML entries,
- finding the most or least active IP addresses,
- finding the longest request.

The program expects log entries in a format similar to:

```text
185.23.54.12 - - [03/Jan/2026:02:14:55 +0100] "GET /home HTTP/1.1" 200 1823
```

---

## 3. Main data structure

### `LogEntry`

The `LogEntry` class represents one parsed web server log entry.

Each object stores:

- `ip` - client IP address,
- `timestamp` - date and time of the request,
- `method` - HTTP method, for example `GET` or `POST`,
- `path` - requested resource path,
- `protocol` - HTTP protocol version,
- `status` - HTTP response status code,
- `bytes_sent` - number of bytes sent in the response.

Example:

```python
LogEntry(
    ip="185.23.54.12",
    timestamp=datetime_object,
    method="GET",
    path="/home",
    protocol="HTTP/1.1",
    status=200,
    bytes_sent=1823
)
```

The class also provides helper methods:

- `is_success()` - returns `True` if the status code is in the 2xx range,
- `is_failed()` - returns `True` if the status code is in the 4xx or 5xx range,
- `is_html()` - returns `True` if the requested path ends with `.html`,
- `bytes_in_kb()` - converts `bytes_sent` to kilobytes.

---

## 4. Date and time handling

Lab 5 uses Python's `datetime` module to represent request timestamps.

Reference:

https://docs.python.org/3/library/datetime.html

### `parse_timestamp(ts_string)`

Converts a timestamp from the log file into a Python `datetime` object.

Example input:

```text
[03/Jan/2026:02:14:55 +0100]
```

Example result:

```python
datetime(2026, 1, 3, 2, 14, 55, tzinfo=...)
```

This makes it possible to compare dates and filter requests by time range.

---

## 5. IPv4 handling

Lab 5 uses Python's `ipaddress` module to work with IP addresses and networks.

Reference:

https://docs.python.org/3/library/ipaddress.html

Important classes:

- `IPv4Address` - represents a single IPv4 address,
- `IPv4Network` - represents an IPv4 network.

Examples:

```python
IPv4Address("185.23.54.12")
IPv4Network("185.23.54.0/24")
```

These classes are useful because they allow safe comparison between IP addresses and networks.

---

## 6. Parsing functions

### `parse_line_to_logentry(line)`

Converts one raw log line into a `LogEntry` object.

It extracts:

- IP address,
- timestamp,
- HTTP method,
- path,
- protocol,
- status code,
- bytes sent.

If the line is empty, the function returns `None`.

### `read_log(lines)`

Reads a list of raw log lines and converts them into a list of `LogEntry` objects.

Empty lines are skipped.

Example:

```python
entries = read_log(lines)
```

---

## 7. Display functions

### `display_log(data)`

Prints paths from log entries.

If the request failed with a 4xx or 5xx status code, the path is printed with `!` at the beginning.

Example output:

```text
/home
!/missing-page
/about
```

### `display_statistics(data)`

Prints statistics required by the assignment:

- largest resource,
- number of failed requests,
- total bytes sent,
- total kilobytes sent.

### `print_html_entries(data)`

Prints successfully retrieved `.html` entries.

If there are no HTML entries, it prints:

```text
HTML entries: none
```

---

## 8. Filtering and analysis functions

### `successful_reads(data)`

Returns a list of entries with successful HTTP status codes.

Successful status codes are in the 2xx range.

Example:

```python
successful = successful_reads(data)
```

### `failed_reads(data)`

Returns a list of entries with failed HTTP status codes.

Failed status codes are in the 4xx and 5xx ranges.

### `count_failed_requests(data)`

Returns the number of failed requests.

Internally, it uses `failed_reads(data)`.

### `non_existent(data)`

Returns unique request strings with HTTP status code `404`.

This is used to find resources that were requested but did not exist.

Example returned value:

```python
["GET /missing-page HTTP/1.1"]
```

### `html_entries(data)`

Returns successfully retrieved entries where the requested path ends with `.html`.

---

## 9. IP-related functions

### `requests_per_ip(data)`

Returns a dictionary where:

- the key is an IP address,
- the value is the number of requests made by that IP address.

Example:

```python
{
    IPv4Address("185.23.54.12"): 2,
    IPv4Address("77.91.204.33"): 1
}
```

### `count_requests_by_ip(data, ip_address)`

Returns the number of requests made by one selected IP address.

Example:

```python
count_requests_by_ip(data, "185.23.54.12")
```

### `entries_from_network(data, network_text)`

Returns entries where the IP address belongs to a selected IPv4 network.

Example:

```python
entries_from_network(data, "185.23.54.0/24")
```

This function uses `IPv4Network` to check whether an IP address belongs to a network.

### `ip_find(data, most_active=True)`

Returns IP addresses with the highest or lowest number of requests.

If `most_active=True`, the function returns IP addresses with the largest number of requests.

Example:

```python
ip_find(data)
```

If `most_active=False`, the function returns IP addresses with the smallest number of requests.

Example:

```python
ip_find(data, most_active=False)
```

The function returns a list because more than one IP address can have the same number of requests.

If the input data is empty, the function returns an empty list.

---

## 10. Time filtering

### `display_requests_between(data, start_time, end_time)`

Displays requests made between two datetime values.

Example:

```python
display_requests_between(data, start_time, end_time)
```

If the second datetime is earlier than the first datetime, the function prints a warning and stops.

---

## 11. Byte and resource functions

### `calculate_total_bytes_sent(data)`

Returns the total number of bytes sent in all log entries.

### `convert_bytes_to_kilobytes(total_bytes)`

Converts bytes to kilobytes.

Example:

```python
convert_bytes_to_kilobytes(2048)
```

Result:

```python
2.0
```

### `find_largest_resource(data)`

Returns the `LogEntry` object with the highest `bytes_sent` value.

If the input data is empty, the function returns `None`.

### `longest_request(data)`

Returns the longest request string together with the IP address that made the request.

The request string contains:

```text
METHOD PATH
```

Example returned value:

```python
("POST /api/very/long/login/path", IPv4Address("77.91.204.33"))
```

If the input data is empty, the function returns `None`.

If there is a tie, the function can return the first longest request found.

---

## 12. Logging and command-line usage

The program can be run from the command line and reads log data from standard input.

Example:

```bash
python3 src/lab5.py < src/log.txt
```

To enable debug logging:

```bash
python3 src/lab5.py DEBUG < src/log.txt
```

The logging level is handled by:

- `build_parser()` - creates the argument parser,
- `configure_logging(log_level)` - configures the logging level.

---

## 13. Testing

Lab 5 functions are tested in:

```text
tests/test_lab5.py
```

Run the tests with:

```bash
python3 -m unittest tests/test_lab5.py
```

A successful result should look similar to:

```text
OK
```

---

## 14. Summary

Lab 5 introduces structured processing of web server logs.

The most important concepts are:

- representing log lines as `LogEntry` objects,
- parsing timestamps with `datetime`,
- handling IP addresses and networks with `ipaddress`,
- filtering entries by status code, IP address, network, file type, and time range,
- calculating statistics from parsed log data,
- testing the implemented functions with `unittest`.
