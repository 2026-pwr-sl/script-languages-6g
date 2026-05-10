"""Create and load the Lab 8 JSON configuration file."""

import argparse
import json
from ipaddress import ip_address
from pathlib import Path


CONFIG_FILE = Path(__file__).with_name("config.json")
CONFIG_ENCODING = "utf-8"

LOGGING_LEVELS = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

DEFAULT_CONFIG = {
    "log_file": "access.log",
    "ip_address": "127.0.0.1",
    "logging_level": "INFO",
    "lines_per_page": 10,
    "request_method": "GET",
}


def ask_text(prompt, default="", input_func=input):
    user_input = input_func(f"{prompt} [{default}]: ").strip()
    if user_input:
        return user_input
    return default


def ask_ip_address(input_func=input):
    while True:
        value = ask_text(
            "IP address used to filter displayed requests",
            DEFAULT_CONFIG["ip_address"],
            input_func,
        )

        try:
            ip_address(value)
        except ValueError:
            print("Enter a correct IP address, for example 127.0.0.1.")
        else:
            return value


def ask_logging_level(input_func=input):
    while True:
        value = ask_text(
            "Logging level",
            DEFAULT_CONFIG["logging_level"],
            input_func,
        ).upper()

        if value in LOGGING_LEVELS:
            return value

        allowed_levels = ", ".join(sorted(LOGGING_LEVELS))
        print(f"Enter one of these logging levels: {allowed_levels}.")


def ask_lines_per_page(input_func=input):
    while True:
        value = ask_text(
            "Number of lines displayed at once",
            str(DEFAULT_CONFIG["lines_per_page"]),
            input_func,
        )

        try:
            lines_per_page = int(value)
        except ValueError:
            print("Enter a whole number.")
            continue

        if lines_per_page > 0:
            return lines_per_page

        print("The number of lines must be greater than zero.")


def ask_request_method(input_func=input):
    while True:
        value = ask_text(
            "HTTP request method to display",
            DEFAULT_CONFIG["request_method"],
            input_func,
        ).upper()

        if value in HTTP_METHODS:
            return value

        allowed_methods = ", ".join(sorted(HTTP_METHODS))
        print(f"Enter one of these HTTP methods: {allowed_methods}.")


def collect_config(input_func=input):
    """Ask the user for all configuration values."""
    return {
        "log_file": ask_text(
            "Name of the web server log file",
            DEFAULT_CONFIG["log_file"],
            input_func,
        ),
        "ip_address": ask_ip_address(input_func),
        "logging_level": ask_logging_level(input_func),
        "lines_per_page": ask_lines_per_page(input_func),
        "request_method": ask_request_method(input_func),
    }


def save_config(config, path=CONFIG_FILE, encoding=CONFIG_ENCODING):
    """Save configuration values in JSON format using the selected encoding."""
    path = Path(path)

    with path.open("w", encoding=encoding) as config_file:
        json.dump(config, config_file, indent=4, ensure_ascii=False)
        config_file.write("\n")


def load_config(path=CONFIG_FILE, encoding=CONFIG_ENCODING):
    """Load configuration values from JSON using the selected encoding."""
    path = Path(path)

    with path.open("r", encoding=encoding) as config_file:
        return json.load(config_file)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Create the Lab 8 application configuration file."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(CONFIG_FILE),
        help="Path where the JSON configuration file will be saved.",
    )
    return parser


def main(args=None):
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    config = collect_config()
    save_config(config, parsed_args.output)
    print(f"Configuration saved to {parsed_args.output}")


if __name__ == "__main__":
    main()
