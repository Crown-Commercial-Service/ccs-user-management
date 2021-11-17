import argparse
import boto3
import botocore.exceptions
import logging

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = 'Arguments to download a given file from S3'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--s3-bucket-name',
        help='The name of the S3 bucket to download a given file from',
        dest='s3_bucket_name',
        required=True
    )
    parser.add_argument(
        '--filename-path',
        help='The full path to the file you wish to download from S3',
        dest='filepath_name',
        required=True
    )
    parser.add_argument(
        '--output-filename',
        help='The name you want to give the file when it is downloaded to the current working directory',
        dest='output_filename',
        required=True
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    s3_bucket_name = args.s3_bucket_name
    filepath_name = args.filepath_name
    output_filename = args.output_filename
    return s3_bucket_name, filepath_name, output_filename


def create_s3_client():
    s3_client = boto3.client('s3', region_name='eu-west-2')
    return s3_client


def get_file_from_s3(filepath_name, output_filename, s3_bucket_name, s3_client):
    try:
        logging.info(f'Attempting to download file {filepath_name} - outputting to: {output_filename}')
        s3_client.download_file(s3_bucket_name, filepath_name, output_filename)
        logging.info(f'Successfully downloaded and saved as {output_filename}')
    except botocore.exceptions.ClientError as e:
        logging.error(f'Unable to download {filepath_name}: {e}')
        exit(1)


def download_from_s3():
    s3_bucket_name, filepath_name, output_filename = get_args()
    s3_client = create_s3_client()
    get_file_from_s3(filepath_name=filepath_name, output_filename=output_filename, s3_bucket_name=s3_bucket_name, s3_client=s3_client)


download_from_s3()
