import argparse
import boto3
import logging

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = "Arguments to create an SSM User"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-iam-username",
        help="The name of the IAM User to generate (note: the user will have access to all SSM resources held under this path, e.g. /iam-username/*",
        dest="iam_username",
        required=True,
    )
    parser.add_argument(
        "-iam-policy-name",
        help="The name of the IAM policy to attach to the IAM user (defaults to "
        "CCS-AllProject-ParameterStore-Lockdown-By-Username-Policy)",
        dest="iam_policy_name",
        default="CCS-AllProject-ParameterStore-Lockdown-By-Username-Policy",
        required=False,
    )
    parser.add_argument(
        "-region",
        help="The region in which the IAM user can communicate with SSM (defaults to eu-west-2)",
        dest="region",
        default="eu-west-2",
        required=False,
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    iam_username = args.iam_username
    iam_policy_name = args.iam_policy_name
    region = args.region
    return iam_username, iam_policy_name, region


def create_client(resource_name, region_name):
    try:
        logging.debug(f"Creating client for {resource_name} in {region_name}")
        client = boto3.client(resource_name, region_name=region_name)
        logging.debug(f"Successfully created {resource_name} client in {region_name}")
        return client
    except Exception as ssm_client_exception:
        logging.error(
            f"Failed to create {resource_name} client in {region_name}: {ssm_client_exception}"
        )
        exit(1)


def get_aws_account_id(sts_client):
    try:
        logging.debug(f"Attempting to obtain AWS Account ID")
        aws_account_id = sts_client.get_caller_identity()["Account"]
        logging.debug(f"Successfully obtained AWS Account ID {aws_account_id}")
        return aws_account_id
    except Exception as sts_client_exception:
        logging.error(f"Failed to retrieve aws account id: {sts_client_exception}")
        exit(1)


def create_iam_user(iam_client, iam_username):
    try:
        logging.debug(f"Creating IAM User {iam_username}")
        iam_user = iam_client.create_user(UserName=iam_username)
        logging.info(f"Successfully created IAM User {iam_username}")
        return iam_user
    except Exception as iam_client_exception:
        logging.error(
            f"Failed to create IAM User {iam_username}: {iam_client_exception}"
        )
        exit(1)


def attach_policy_to_iam_user(
    aws_account_id, iam_client, iam_policy_name, iam_username
):
    target_policy_arn = f"arn:aws:iam::{aws_account_id}:policy/{iam_policy_name}"
    logging.debug(f"Target Policy ARN is: {target_policy_arn}")
    try:
        logging.debug(
            f"Attempting to attach policy {iam_policy_name} to IAM user {iam_username}"
        )
        iam_client.attach_user_policy(
            UserName=iam_username, PolicyArn=target_policy_arn
        )
        logging.info(
            f"Successfully attached IAM policy {iam_policy_name} to {iam_username}"
        )
    except Exception as iam_policy_attachment_exception:
        logging.error(
            f"Failed to attach IAM policy {iam_policy_name} to {iam_username}: {iam_policy_attachment_exception}"
        )
        exit(1)


def create_access_keys_for_iam_user(iam_client, iam_username):
    try:
        logging.debug(f"Attempting to create access keys for IAM user {iam_username}")
        access_keys_response = iam_client.create_access_key(UserName=iam_username)
        logging.info(f"Created access keys for IAM user {iam_username}")
        access_key_id = access_keys_response["AccessKey"]["AccessKeyId"]
        secret_access_key_id = access_keys_response["AccessKey"]["SecretAccessKey"]
        return access_key_id, secret_access_key_id
    except Exception as access_key_exception:
        logging.error(
            f"Failed to create access keys for IAM user {iam_username}: {access_key_exception}"
        )
        exit(1)


def iam_user_handler(aws_account_id, iam_client, iam_policy_name, iam_username):
    create_iam_user_response = create_iam_user(
        iam_client=iam_client, iam_username=iam_username
    )
    iam_user = create_iam_user_response["User"]["UserName"]
    attach_policy_to_iam_user(
        aws_account_id=aws_account_id,
        iam_client=iam_client,
        iam_policy_name=iam_policy_name,
        iam_username=iam_user,
    )
    access_key, secret_access_key = create_access_keys_for_iam_user(
        iam_client=iam_client, iam_username=iam_username
    )
    return access_key, secret_access_key


def create_boto3_clients(region):
    iam_client = create_client(resource_name="iam", region_name=region)
    sts_client = create_client(resource_name="sts", region_name=region)
    secrets_manager_client = create_client(
        resource_name="secretsmanager", region_name=region
    )
    return iam_client, sts_client, secrets_manager_client


def create_secrets_manager_resource(
    iam_username, secrets_manager_client, secret_name, secret_value
):
    try:
        logging.debug(f"Attempting to create secrets manager resource: {secret_name}")
        secrets_manager_client.create_secret(
            Name=f"{iam_username}/{secret_name}", SecretString=secret_value
        )
        logging.info(
            f"Successfully created secrets manager resource {secret_name} and obtained ARN"
        )
    except Exception as secrets_manager_exception:
        logging.error(
            f"Failed to create secrets manager resource {secret_name}: {secrets_manager_exception}"
        )
        exit(1)


def create_dict_for_secrets_manager_resources(
    aws_access_key, aws_region, aws_secret_access_key
):
    secrets_manager_resources_dict = {
        "aws_region": aws_region,
        "aws_access_key": aws_access_key,
        "aws_secret_access_key": aws_secret_access_key,
    }
    return secrets_manager_resources_dict


def upload_secrets_manager_resources(
    iam_username, secrets_manager_client, secrets_manager_resources_dict
):
    for secrets_manager_resource in secrets_manager_resources_dict:
        create_secrets_manager_resource(
            iam_username=iam_username,
            secrets_manager_client=secrets_manager_client,
            secret_name=secrets_manager_resource,
            secret_value=secrets_manager_resources_dict[secrets_manager_resource],
        )
    logging.info(
        f"Finished uploading secrets manager resources required for IAM user {iam_username}"
    )


def create_ssm_user():
    iam_username, iam_policy_name, region = get_args()
    iam_client, sts_client, secrets_manager_client = create_boto3_clients(region=region)
    aws_account_id = get_aws_account_id(sts_client=sts_client)
    access_key, secret_access_key = iam_user_handler(
        aws_account_id=aws_account_id,
        iam_client=iam_client,
        iam_policy_name=iam_policy_name,
        iam_username=iam_username,
    )
    secrets_manager_resources_dict = create_dict_for_secrets_manager_resources(
        aws_access_key=access_key,
        aws_region=region,
        aws_secret_access_key=secret_access_key,
    )
    upload_secrets_manager_resources(
        iam_username=iam_username,
        secrets_manager_client=secrets_manager_client,
        secrets_manager_resources_dict=secrets_manager_resources_dict,
    )


create_ssm_user()
