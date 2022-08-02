import argparse
import logging
from notifications_python_client.notifications import NotificationsAPIClient

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = "Arguments to manage Auth0 users who do not have MFA enabled"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--api-key",
        help="The API Key needed to authenticate with Gov UK Notify",
        dest="api_key",
        required=True,
    )
    parser.add_argument(
        "--auth0-tenant",
        help="The name of the Auth0 Tenant",
        dest="auth0_tenant",
        required=True,
    )
    parser.add_argument(
        "--mfa-disabled-users",
        help="Comma separated list of Auth0 users who do not have MFA enabled",
        dest="mfa_disabled_users",
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
    api_key = args.api_key
    auth0_tenant = args.auth0_tenant
    mfa_disabled_users = args.mfa_disabled_users
    template_id = args.template_id
    return api_key, auth0_tenant, mfa_disabled_users, template_id


def check_auth0_user_has_email_address(auth0_user):
    if "@" in auth0_user:
        return True
    else:
        return False


def send_email_via_notify(api_key, email_address, auth0_tenant, template_id):
    notifications_client = NotificationsAPIClient(api_key)
    notifications_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation={"auth0_user": email_address, "auth0_tenant": auth0_tenant},
    )


def send_email_handler():
    api_key, auth0_tenant, mfa_disabled_users, template_id = get_args(
        args=parse_arguments()
    )
    for auth0_user in mfa_disabled_users.split(","):
        user_has_email_address = check_auth0_user_has_email_address(auth0_user=auth0_user)
        if user_has_email_address:
            logging.info(
                f"Sending email notification to {auth0_user} to request MFA is enabled"
            )
            send_email_via_notify(
                api_key=api_key,
                auth0_tenant=auth0_tenant,
                email_address=auth0_user,
                template_id=template_id
            )
            logging.info(f"Email sent to {auth0_user} regarding MFA")
        else:
            logging.info(f"{auth0_user} does not appear to be in an email address format, no email to be sent")


send_email_handler()
