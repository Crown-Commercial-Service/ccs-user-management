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
        "--warning-threshold",
        help="The threshold within which users receive a warning for stale activity, but do not get removed",
        dest="warning_threshold",
        default=80,
        required=False,
    )
    parser.add_argument(
        "--deletion-threshold",
        help="The threshold within which users are automatically removed (and notified that their account is removed)",
        dest="deletion_threshold",
        default=90,
        required=False,
    )
    parser.add_argument(
        "--api-key-resource-name",
        help="The name of the API Key resource in Secrets Manager",
        dest="api_key_resource_name",
        default="ccs_user_management_notify_api_key",
        required=False,
    )
    parser.add_argument(
        "--deletion-template-resource-name",
        help="The name of the deletion template resource in Secrets Manager",
        dest="deletion_template_resource_name",
        default="ccs_user_management_notify_deletion_template",
        required=False,
    )
    parser.add_argument(
        "--warning-template-resource-name",
        help="The name of the warning template resource in Secrets Manager",
        dest="warning_template_resource_name",
        default="ccs_user_management_notify_warning_template",
        required=False,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    csv_filename = args.csv_filename
    ignore_list = args.ignore_list
    warning_threshold = args.warning_threshold
    deletion_threshold = args.deletion_threshold
    api_key_resource_name = args.api_key_resource_name
    deletion_template_resource_name = args.deletion_template_resource_name
    warning_template_resource_name = args.warning_template_resource_name
    return (
        csv_filename,
        ignore_list,
        warning_threshold,
        deletion_threshold,
        api_key_resource_name,
        deletion_template_resource_name,
        warning_template_resource_name,
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


def check_action_to_be_taken_on_user(
    deletion_threshold, iam_username, number_of_inactive_days, warning_threshold
):
    if number_of_inactive_days >= deletion_threshold:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days} days, and should therefore be deleted"
        )
        action_to_be_taken = "deletion"
    elif number_of_inactive_days >= warning_threshold:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days} days, and should therefore be warned"
        )
        action_to_be_taken = "warning"
    else:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days} days, no action needed"
        )
        action_to_be_taken = False
    return action_to_be_taken


def create_iam_client():
    try:
        logging.debug('Creating IAM Client')
        iam_client = boto3.client("iam", region_name="eu-west-2")
        logging.debug('Successfully created IAM Client')
        return iam_client
    except botocore.exceptions.ClientError as e:
        logging.error(f'Unable to create IAM Client: {e}')
        exit(1)


def delete_iam_user(aws_account, iam_client, iam_user):
    try:
        logging.info(f'Attempting to delete IAM user {iam_user} from AWS account: {aws_account}')
        iam_client.delete_user(UserName=iam_user)
        logging.info(f'IAM user {iam_user} has been deleted from AWS account: {aws_account}')
    except botocore.exceptions.ClientError as e:
        logging.error(f'Unable to delete IAM user {iam_user}: {e}')
        exit(1)


def create_secretsmanager_client():
    secretsmanager_client = boto3.client("secretsmanager", region_name="eu-west-2")
    return secretsmanager_client


def get_secret_from_secretsmanager(secretsmanager_client, secret_name):
    secret = secretsmanager_client.get_secret_value(SecretId=secret_name)
    return secret['SecretString']


def configure_secretsmanager_resources(
    api_key_resource_name,
    deletion_template_resource_name,
    warning_template_resource_name,
):
    secretsmanager_client = create_secretsmanager_client()
    api_key = get_secret_from_secretsmanager(
        secretsmanager_client=secretsmanager_client, secret_name=api_key_resource_name
    )
    deletion_template = get_secret_from_secretsmanager(
        secretsmanager_client=secretsmanager_client,
        secret_name=deletion_template_resource_name,
    )
    warning_template = get_secret_from_secretsmanager(
        secretsmanager_client=secretsmanager_client,
        secret_name=warning_template_resource_name,
    )
    return api_key, deletion_template, warning_template


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


def csv_file_handler(
    api_key_resource_name,
    csv_filename,
    deletion_template_resource_name,
    deletion_threshold,
    ignore_list,
    warning_threshold,
    warning_template_resource_name,
):
    api_key, deletion_template, warning_template = configure_secretsmanager_resources(
        api_key_resource_name=api_key_resource_name,
        deletion_template_resource_name=deletion_template_resource_name,
        warning_template_resource_name=warning_template_resource_name,
    )
    iam_client = create_iam_client()

    with open(csv_filename) as stale_iam_users_file:
        csv_reader = csv.reader(stale_iam_users_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                logging.info(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                account_id = row[0]
                iam_username = row[1]
                inactivity_in_days = row[2]
                user_in_ignore_list = check_if_user_in_ignore_list(
                    iam_username=iam_username, ignore_list=ignore_list
                )
                if user_in_ignore_list:
                    logging.info(" ")
                    logging.info(
                        f"User {iam_username} is in the ignore list, no action required"
                    )
                else:
                    logging.info(f"Proceeding with relevant action for {iam_username}")
                    number_of_inactive_days = get_number_of_inactive_days_for_user(
                        inactivity_in_days=inactivity_in_days
                    )
                    action_to_be_taken = check_action_to_be_taken_on_user(
                        deletion_threshold=deletion_threshold,
                        iam_username=iam_username,
                        number_of_inactive_days=number_of_inactive_days,
                        warning_threshold=warning_threshold,
                    )
                    if action_to_be_taken == "deletion":
                        delete_iam_user(aws_account=account_id, iam_client=iam_client, iam_user=iam_username)
                        send_email_via_notify(
                            api_key=api_key,
                            aws_account=account_id,
                            email_address=iam_username,
                            inactive_number_of_days=number_of_inactive_days,
                            max_number_of_days=deletion_threshold,
                            template_id=deletion_template,
                        )
                        logging.info(
                            f"Deletion notification email sent to user {iam_username} for AWS Account: {account_id}"
                        )
                        continue
                    elif action_to_be_taken == "warning":
                        send_email_via_notify(
                            api_key=api_key,
                            aws_account=account_id,
                            email_address=iam_username,
                            inactive_number_of_days=number_of_inactive_days,
                            max_number_of_days=deletion_threshold,
                            template_id=warning_template,
                        )
                        logging.info(
                            f"Warning notification email sent to user {iam_username} for AWS Account: {account_id}"
                        )
                    else:
                        logging.info(
                            f"No notification email needs to be sent to user {iam_username} for AWS Account: {account_id}"
                        )
                line_count += 1


def stale_iam_users():
    (
        csv_filename,
        ignore_list,
        warning_threshold,
        deletion_threshold,
        api_key_resource_name,
        deletion_template_resource_name,
        warning_template_resource_name,
    ) = get_args()
    csv_file_handler(
        api_key_resource_name=api_key_resource_name,
        csv_filename=csv_filename,
        deletion_template_resource_name=deletion_template_resource_name,
        deletion_threshold=int(deletion_threshold),
        ignore_list=ignore_list,
        warning_threshold=int(warning_threshold),
        warning_template_resource_name=warning_template_resource_name,
    )


stale_iam_users()
