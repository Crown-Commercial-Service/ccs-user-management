import argparse
import boto3
import logging

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = "Arguments to cleanup the CCS User Management S3 Bucket"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--bucket-name",
        help="The name of the S3 Bucket for User Management",
        dest="bucket_name",
        required=True,
    )
    parser.add_argument(
        "--bucket-paths",
        help="Comma separated list of bucket paths to cleanup for the CCS User Management S3 bucket",
        dest="bucket_paths",
        required=True,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    bucket_name = args.bucket_name
    bucket_paths = args.bucket_paths.split(",")
    return bucket_name, bucket_paths


def create_s3_client():
    client = boto3.client('s3')
    return client


def delete_all_files_within_folder(s3_client, bucket_name, bucket_path):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=bucket_path)
    response_contents = response['Contents']
    logging.info(f"Checking for content in {bucket_path} folder for {bucket_name}")
    for response_content in response_contents:
        if response_content['Key'] == f"{bucket_path}/":
            logging.debug(f"Not deleting folder path: {bucket_path}")
        else:
            logging.info(f"Found {response_content['Key']} in S3 bucket {bucket_name}")
            delete_file_within_folder(s3_client=s3_client, bucket_name=bucket_name, bucket_resource=response_content['Key'])


def delete_file_within_folder(s3_client, bucket_name, bucket_resource):
    try:
        logging.debug(f"Deleting {bucket_resource} from S3 Bucket: {bucket_name}")
        s3_client.delete_object(Bucket=bucket_name, Key=bucket_resource)
        logging.info(f"Successfully deleted {bucket_resource}")
    except Exception as e:
        logging.error(f"Failed to delete {bucket_resource} from S3 Bucket: {bucket_name}: {e}")
        exit(1)


def user_management_bucket_cleanup():
    bucket_name, bucket_paths = get_args()
    s3_client = create_s3_client()
    for bucket_path in bucket_paths:
        delete_all_files_within_folder(s3_client=s3_client, bucket_name=bucket_name, bucket_path=bucket_path)


user_management_bucket_cleanup()
