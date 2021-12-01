import argparse
import logging
from notifications_python_client.notifications import NotificationsAPIClient

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = "Arguments to manage stale IAM users"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--account-id",
        help="The name of the relevant user account ID",
        dest="account_id",
        required=True,
    )
    parser.add_argument(
        "--api-key",
        help="The API Key needed to authenticate with Gov UK Notify",
        dest="api_key",
        required=True,
    )
    parser.add_argument(
        "--days-inactive",
        help="The number of days that the relevant account has been inactive",
        dest="days_inactive",
        required=True,
    )
    parser.add_argument(
        "--deletion-threshold",
        help="The threshold at which a user should be deleted",
        dest="deletion_threshold",
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
        "--template-id",
        help="The ID of the template to use in order to send emails via Gov UK Notify",
        dest="template_id",
        required=True,
    )
    parser.add_argument(
        "--username",
        help="The name of the relevant IAM user",
        dest="username",
        required=True,
    )
    parser.add_argument(
        "--warning-threshold",
        help="The threshold at which a user should be warned",
        dest="warning_threshold",
        required=True,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    account_id = args.account_id
    api_key = args.api_key
    days_inactive = args.days_inactive
    deletion_threshold = args.deletion_threshold
    ignore_list = args.ignore_list
    template_id = args.template_id
    username = args.username
    warning_threshold = args.warning_threshold
    return (
        account_id,
        api_key,
        days_inactive,
        deletion_threshold,
        ignore_list,
        template_id,
        username,
        warning_threshold,
    )


def check_if_user_in_ignore_list(iam_username, ignore_list):
    users_to_ignore = ignore_list.split(",")
    if users_to_ignore:
        for user_to_ignore in users_to_ignore:
            if user_to_ignore == iam_username:
                user_should_be_ignored = True
                return user_should_be_ignored


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


def check_iam_user_has_email_address(iam_user):
    if "@" in iam_user:
        return True
    else:
        return False
