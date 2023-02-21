import argparse
import csv
import logging

logging.basicConfig(level=logging.INFO)


def parse_get_inactive_iam_users_arguments():
    description = "Arguments to get list of IAM users"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--csv-filename",
        help="The name of the CSV file containing stale IAM users",
        dest="csv_filename",
        required=True,
    )
    return parser.parse_args()


def get_inactive_iam_users_args(args=parse_get_inactive_iam_users_arguments()):
    csv_filename = args.csv_filename
    return csv_filename


def get_inactive_iam_users(csv_filename):
    inactive_iam_users = {}
    with open(csv_filename) as inactive_iam_users_file:
        csv_reader = csv.reader(inactive_iam_users_file, delimiter=",")
        for row in csv_reader:
            account_id = row[0]
            iam_username = row[1]
            inactivity_in_days = row[2]
            inactive_iam_users[iam_username] = {}
            inactive_iam_users[iam_username].update({"account_id": account_id})
            inactive_iam_users[iam_username].update(
                {"inactivity_in_days": inactivity_in_days}
            )
    return inactive_iam_users


def get_inactive_iam_users_handler():
    csv_filename = get_inactive_iam_users_args()
    inactive_iam_users = get_inactive_iam_users(csv_filename=csv_filename)
    print(inactive_iam_users)
    return inactive_iam_users


get_inactive_iam_users_handler()
