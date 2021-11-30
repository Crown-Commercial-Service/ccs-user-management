import argparse


def parse_inactive_days_arguments():
    description = "Arguments to manage stale IAM users"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--inactivity-in-days-string",
        help="The string response for inactivity in days, to be converted into a single int value",
        dest="inactivity_in_days_string",
        required=True,
    )
    return parser.parse_args()


def get_inactive_days_args(args=parse_inactive_days_arguments()):
    inactivity_in_days_string = args.inactivity_in_days_string
    return inactivity_in_days_string


def get_number_of_inactive_days_for_user(inactivity_in_days):
    number_of_inactive_days = int(
        "".join(list(filter(str.isdigit, inactivity_in_days)))
    )
    print(number_of_inactive_days)
    return number_of_inactive_days


def get_days_inactive():
    inactivity_in_days = get_inactive_days_args()
    get_number_of_inactive_days_for_user(inactivity_in_days=inactivity_in_days)


get_days_inactive()
