import argparse
import boto3
import botocore.exceptions
import logging

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = (
        "Arguments to obtain a list of files for triggering the Inactive IAM Users job"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--s3-bucket-name",
        help="The name of the S3 bucket containing the list of files",
        dest="s3_bucket_name",
        required=True,
    )
    parser.add_argument(
        "--folder-path",
        help="The folder path containing the list of files",
        dest="folder_path",
        default="expired_iam_users/",
        required=False,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    s3_bucket_name = args.s3_bucket_name
    folder_path = args.folder_path
    return s3_bucket_name, folder_path


def create_s3_client():
    s3_client = boto3.client("s3", region_name="eu-west-2")
    return s3_client


def get_list_of_files_from_s3(folder_path, s3_bucket_name, s3_client):
    try:
        list_of_files_from_s3 = []
        logging.info(
            f"Attempting to obtain list of files from path {folder_path} in {s3_bucket_name}"
        )
        objects_in_path = s3_client.list_objects(
            Bucket=s3_bucket_name, Prefix=folder_path
        )
        for object in objects_in_path["Contents"]:
            list_of_files_from_s3.append(object["Key"])
        for file in list_of_files_from_s3:
            if file == folder_path:
                logging.debug(
                    f"Removing returned object that matches folder path {folder_path}"
                )
                list_of_files_from_s3.remove(file)
        logging.info("List of files successfully obtained")
        return list_of_files_from_s3
    except botocore.exceptions.ClientError as e:
        logging.error(
            f"Unable to obtain list of files in {folder_path} path for {s3_bucket_name}: {e}"
        )
        exit(1)


def download_from_s3():
    s3_bucket_name, folder_path = get_args()
    s3_client = create_s3_client()
    list_of_files_from_s3 = get_list_of_files_from_s3(
        folder_path=folder_path, s3_bucket_name=s3_bucket_name, s3_client=s3_client
    )
    print(list_of_files_from_s3)
    return list_of_files_from_s3


download_from_s3()
