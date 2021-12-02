import argparse
from iam_common import create_iam_client, delete_iam_user_handler


def parse_delete_iam_user_arguments():
    description = "Arguments to delete an IAM user"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--aws-account",
        help="The name of the AWS account in which to delete the IAM user",
        dest="aws_account",
        required=True,
    )
    parser.add_argument(
        "--iam-user",
        help="The name of the IAM user to delete",
        dest="iam_user",
        required=True,
    )
    return parser.parse_args()


def get_delete_iam_users_args(args=parse_delete_iam_user_arguments()):
    aws_account = args.aws_account
    iam_user = args.iam_user
    return aws_account, iam_user


def delete_iam_user():
    aws_account, iam_user = get_delete_iam_users_args()
    iam_client = create_iam_client()
    iam_user_deleted = delete_iam_user_handler(
        aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
    )


delete_iam_user()
