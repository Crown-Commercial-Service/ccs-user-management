import argparse
import logging
from notifications_python_client.notifications import NotificationsAPIClient

logging.basicConfig(level=logging.INFO)


def parse_warn_no_mfa_user_arguments():
    description = "Arguments to warn a user that does not have MFA enabled"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--api-key",
        help="The API Key used to integrate with Gov UK Notify",
        dest="api_key",
        required=True,
    )
    parser.add_argument(
        "--aws-account",
        help="The AWS Account for the user that does not have MFA enabled",
        dest="aws_account",
        required=True,
    )
    parser.add_argument(
        "--template-id",
        help="The Gov UK Notify template ID used to send notifications r.e. No MFA",
        dest="template_id",
        required=True,
    )
    parser.add_argument(
        "--username",
        help="The AWS username for the user that does not have MFA enabled",
        dest="username",
        required=True,
    )
    return parser.parse_args()


def get_warn_no_mfa_user_args(args=parse_warn_no_mfa_user_arguments()):
    account_id = args.aws_account
    api_key = args.api_key
    template_id = args.template_id
    username = args.username
    return account_id, api_key, template_id, username


def check_iam_user_has_email_address(iam_user):
    if "@" in iam_user:
        return True
    else:
        return False


def send_no_mfa_notify_email(api_key, aws_account, email_address, template_id):
    notifications_client = NotificationsAPIClient(api_key)
    notifications_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation={
            "aws_account": aws_account,
            "iam_user": email_address,
        },
    )


def warn_no_mfa_user():
    account_id, api_key, template_id, username = get_warn_no_mfa_user_args()
    user_has_email_address = check_iam_user_has_email_address(iam_user=username)
    if user_has_email_address:
        logging.info(
            f"Sending email notification to {username} regarding lack of MFA on {account_id}"
        )
        send_no_mfa_notify_email(
            api_key=api_key,
            aws_account=account_id,
            email_address=username,
            template_id=template_id
        )
        logging.info(
            f"Email sent to {username} regarding lack of MFA on {account_id}"
        )
    else:
        logging.info(
            f"{username} does not appear to be in an email address format, no email to be sent"
        )


warn_no_mfa_user()
