import logging
from inactive_users_common import *
from iam_common import *

logging.basicConfig(level=logging.INFO)


def check_if_user_in_deletion_threshold(days_inactive, deletion_threshold, username):
    if int(days_inactive) >= int(deletion_threshold):
        logging.info(
            f"The access keys for {username} have been inactive for {days_inactive} days and should be deleted"
        )
        action_to_be_taken = True
    else:
        logging.info(
            f"The access keys for {username} have been in active for {days_inactive}, which is not within the deletion"
            f" threshold of {deletion_threshold} days"
        )
        action_to_be_taken = False
    return action_to_be_taken


def delete_iam_user_access_keys():
    (
        account_id,
        api_key,
        days_inactive,
        deletion_threshold,
        ignore_list,
        template_id,
        username,
        warning_threshold,
    ) = get_args()
    user_in_ignore_list = check_if_user_in_ignore_list(
        iam_username=username, ignore_list=ignore_list
    )
    if user_in_ignore_list:
        logging.info(f"User {username} is in the ignore list, so no action to be taken")
    else:
        user_in_deletion_threshold = check_if_user_in_deletion_threshold(
            days_inactive=days_inactive,
            deletion_threshold=deletion_threshold,
            username=username,
        )
        if user_in_deletion_threshold:
            logging.info(
                f"Proceeding with access key deletion for {username} in {account_id}"
            )
            iam_client = create_iam_client()
            access_key_deleted = delete_user_access_keys(
                aws_account=account_id, iam_client=iam_client, iam_user=username
            )
            if access_key_deleted:
                user_has_email_address = check_iam_user_has_email_address(
                    iam_user=username
                )
                if user_has_email_address:
                    logging.info(
                        f"Sending email notification to {username} regarding inactivity on {account_id}"
                    )
                    send_email_via_notify(
                        api_key=api_key,
                        aws_account=account_id,
                        email_address=username,
                        inactive_number_of_days=days_inactive,
                        max_number_of_days=deletion_threshold,
                        template_id=template_id,
                    )
                    logging.info(
                        f"Email sent to {username} regarding inactivity on {account_id}"
                    )
                else:
                    logging.info(
                        f"{username} does not appear to be in an email address format, no email to be sent"
                    )
            else:
                logging.info(
                    f"Not sending email notification to {username} regarding inactivity on {account_id} as account was "
                    f"not deleted/removed"
                )


delete_iam_user_access_keys()
