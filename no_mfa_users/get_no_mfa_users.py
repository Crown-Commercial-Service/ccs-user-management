import argparse
import csv
import logging

logging.basicConfig(level=logging.INFO)


def parse_get_no_mfa_users_arguments():
    description = "Arguments to get list of IAM users without MFA enabled"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--csv-filename",
        help="The name of the CSV file containing stale IAM users",
        dest="csv_filename",
        required=True,
    )
    return parser.parse_args()


def get_no_mfa_users_args(args=parse_get_no_mfa_users_arguments()):
    csv_filename = args.csv_filename
    return csv_filename


def get_no_mfa_users(csv_filename):
    no_mfa_users = {}
    with open(csv_filename) as no_mfa_users_file:
        csv_reader = csv.reader(no_mfa_users_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                account_id = row[0]
                iam_username = row[2]
                no_mfa_users[iam_username] = {}
                no_mfa_users[iam_username].update({"account_id": account_id})
    return no_mfa_users


def get_no_mfa_users_handler():
    csv_filename = get_no_mfa_users_args()
    no_mfa_users = get_no_mfa_users(csv_filename=csv_filename)
    print(no_mfa_users)
    return no_mfa_users


get_no_mfa_users_handler()
