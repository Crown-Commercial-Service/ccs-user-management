import logging
from inactive_users_common import *
from delete_iam_user import *

logging.basicConfig(level=logging.INFO)


def delete_iam_users():
    (csv_filename, ignore_list, threshold, api_key, template_id) = get_args()
    dict_of_users = get_inactive_iam_users(csv_filename=csv_filename)
    for user in dict_of_users:
        account_id = dict_of_users[user]["account_id"]
        inactivity_in_days = dict_of_users[user]["inactivity_in_days"]
        user_in_ignore_list = check_if_user_in_ignore_list(
            iam_username=user, ignore_list=ignore_list
        )
        if user_in_ignore_list:
            logging.info(f"User {user} is in the ignore list, so no action to be taken")
        else:
            number_of_inactive_days = int(
                get_number_of_inactive_days_for_user(
                    inactivity_in_days=inactivity_in_days
                )
            )
            user_breaches_threshold = check_if_user_breaches_threshold(
                iam_username=user,
                number_of_inactive_days=number_of_inactive_days,
                threshold=int(threshold),
            )
            if user_breaches_threshold:
                logging.info(
                    f"Proceeding with IAM account deletion for {user} in {account_id}"
                )
                iam_client = create_iam_client()
                iam_user_deleted = delete_iam_user(
                    aws_account=account_id, iam_client=iam_client, iam_user=user
                )
                if iam_user_deleted:
                    user_has_email_address = check_iam_user_has_email_address(
                        iam_user=user
                    )
                    if user_has_email_address:
                        logging.info(
                            f"Sending email notification to {user} regarding inactivity on {account_id}"
                        )
                        send_email_via_notify(
                            api_key=api_key,
                            aws_account=account_id,
                            email_address=user,
                            inactive_number_of_days=number_of_inactive_days,
                            max_number_of_days=threshold,
                            template_id=template_id,
                        )
                        logging.info(
                            f"Email sent to {user} regarding inactivity on {account_id}"
                        )
                    else:
                        logging.info(
                            f"{user} does not appear to be in an email address format, no email to be sent"
                        )
                else:
                    logging.info(
                        f"Not sending email notification to {user} regarding inactivity on {account_id} as account was "
                        f"not deleted/removed"
                    )


delete_iam_users()
