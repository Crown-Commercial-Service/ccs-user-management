import argparse
import boto3
import botocore.exceptions
import csv
import logging
from notifications_python_client.notifications import NotificationsAPIClient

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = "Arguments to manage stale IAM users"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--csv-filename",
        help="The name of the CSV file containing stale IAM users",
        dest="csv_filename",
        required=True,
    )
    parser.add_argument(
        "--ignore-list",
        help="Comma separated containing IAM users to ignore/exclude when filtering through stale users",
        dest="ignore_list",
        default="",
        required=False,
    )
    parser.add_argument(
        "--threshold",
        help="The threshold at which action needs to be taken against a given user",
        dest="threshold",
        required=True,
    )
    parser.add_argument(
        "--api-key",
        help="The API Key needed to authenticate with Gov UK Notify",
        dest="api_key",
        required=True,
    )
    parser.add_argument(
        "--template-id",
        help="The ID of the template to use in order to send emails via Gov UK Notify",
        dest="template_id",
        required=True,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    csv_filename = args.csv_filename
    ignore_list = args.ignore_list
    threshold = args.threshold
    api_key = args.api_key
    template_id = args.template_id
    return (
        csv_filename,
        ignore_list,
        threshold,
        api_key,
        template_id,
    )


def check_if_user_in_ignore_list(iam_username, ignore_list):
    users_to_ignore = ignore_list.split(",")
    if users_to_ignore:
        for user_to_ignore in users_to_ignore:
            if user_to_ignore == iam_username:
                user_should_be_ignored = True
                return user_should_be_ignored


def get_number_of_inactive_days_for_user(inactivity_in_days):
    number_of_inactive_days = int(
        "".join(list(filter(str.isdigit, inactivity_in_days)))
    )
    return number_of_inactive_days


def check_if_user_breaches_threshold(iam_username, number_of_inactive_days, threshold):
    if number_of_inactive_days >= threshold:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days} days"
        )
        action_to_be_taken = True
    else:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days}, which is not in the {threshold} threshold"
        )
        action_to_be_taken = False
    return action_to_be_taken


def send_email_via_notify(
    api_key,
    aws_account,
    email_address,
    inactive_number_of_days,
    max_number_of_days,
    template_id,
):
    notifications_client = NotificationsAPIClient(api_key)
    notifications_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation={
            "aws_account": aws_account,
            "iam_user": email_address,
            "inactive_number_of_days": inactive_number_of_days,
            "max_number_of_days": max_number_of_days,
        },
    )


def get_inactive_iam_users(csv_filename):
    inactive_iam_users = {}
    with open(csv_filename) as inactive_iam_users_file:
        csv_reader = csv.reader(inactive_iam_users_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                account_id = row[0]
                iam_username = row[1]
                inactivity_in_days = row[2]
                inactive_iam_users[iam_username] = {}
                inactive_iam_users[iam_username].update({"account_id": account_id})
                inactive_iam_users[iam_username].update(
                    {"inactivity_in_days": inactivity_in_days}
                )
    return inactive_iam_users
