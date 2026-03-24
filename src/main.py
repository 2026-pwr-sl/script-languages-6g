import argparse

from team import count_team_members, team_data
from utils import display_team_members, format_greeting


def build_parser():
    parser = argparse.ArgumentParser(
        description="Simple CLI for the 6g team project."
    )
    parser.add_argument(
        "--show-team",
        action="store_true",
        help="Display all team members.",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Display the number of team members.",
    )
    parser.add_argument(
        "--greet",
        metavar="NAME",
        help="Print a greeting for the provided name.",
    )
    return parser


def main(args=None):
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not any(
        [parsed_args.show_team, parsed_args.count, parsed_args.greet]
    ):
        parser.print_help()
        return

    if parsed_args.show_team:
        display_team_members(team_data)

    if parsed_args.count:
        print(
            "Number of team members: "
            f"{count_team_members(team_data)}"
        )

    if parsed_args.greet:
        print(format_greeting(parsed_args.greet))


if __name__ == "__main__":
    main()
