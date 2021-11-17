import argparse
import csv
import logging

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
        default=105,
        required=False,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    csv_filename = args.csv_filename
    ignore_list = args.ignore_list
    warning_threshold = args.warning_threshold
    deletion_threshold = args.deletion_threshold
    return csv_filename, ignore_list, warning_threshold, deletion_threshold


def csv_file_handler(csv_filename, ignore_list, warning_threshold, deletion_threshold):
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
                    check_action_to_be_taken_on_user(
                        deletion_threshold=deletion_threshold,
                        iam_username=iam_username,
                        number_of_inactive_days=number_of_inactive_days,
                        warning_threshold=warning_threshold,
                    )
                line_count += 1


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
    elif number_of_inactive_days >= warning_threshold:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days} days, and should therefore be warned"
        )
    else:
        logging.info(
            f"{iam_username} has been inactive for {number_of_inactive_days} days, no action needed"
        )


def stale_iam_users():
    csv_filename, ignore_list, warning_threshold, deletion_threshold = get_args()
    csv_file_handler(
        csv_filename=csv_filename,
        deletion_threshold=int(deletion_threshold),
        ignore_list=ignore_list,
        warning_threshold=int(warning_threshold),
    )


stale_iam_users()
