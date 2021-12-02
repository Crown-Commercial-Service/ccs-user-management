import boto3
import botocore.exceptions
import logging

logging.basicConfig(level=logging.INFO)


def create_iam_client():
    try:
        logging.debug("Creating IAM Client")
        iam_client = boto3.client("iam", region_name="eu-west-2")
        logging.debug("Successfully created IAM Client")
        return iam_client
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to create IAM Client: {e}")
        exit(1)


def check_if_user_exists(aws_account, iam_client, iam_user):
    try:
        logging.debug(
            f"Checking to see if user {iam_user} exists in AWS account: {aws_account}"
        )
        iam_client.get_user(UserName=iam_user)
        return True
    except iam_client.exceptions.NoSuchEntityException:
        logging.debug(
            f"User {iam_user} does exist in {aws_account}, no action to be taken"
        )
        return False
    except botocore.exceptions.ClientError as e:
        logging.error(
            f"Unable to check if IAM user {iam_user} exists in {aws_account}: {e}"
        )
        exit(1)


def delete_iam_login_profile(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Attempting to delete IAM login profile for {iam_user} from AWS account: {aws_account}"
        )
        iam_client.delete_login_profile(UserName=iam_user)
        logging.info(
            f"IAM login profile {iam_user} has been deleted from AWS account: {aws_account}"
        )
    except iam_client.exceptions.NoSuchEntityException:
        logging.info(
            f"User {iam_user} does not have a login profile associated with their IAM user, continuing"
        )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete IAM login profile {iam_user}: {e}")
        exit(1)


def delete_user_access_keys(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for access keys associated with {iam_user} in AWS account: {aws_account}"
        )
        access_keys = iam_client.list_access_keys(UserName=iam_user)
        user_access_keys = access_keys["AccessKeyMetadata"]
        if user_access_keys:
            for user_access_key in user_access_keys:
                iam_client.delete_access_key(
                    UserName=iam_user, AccessKeyId=user_access_key["AccessKeyId"]
                )
            logging.info(
                f"Deleted all access keys associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No access keys found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete access keys for user {iam_user}: {e}")
        exit(1)


def delete_user_signing_certificates(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for signing certificates associated with {iam_user} in AWS account: {aws_account}"
        )
        signing_certificates = iam_client.list_signing_certificates(UserName=iam_user)
        user_signing_certificates = signing_certificates["Certificates"]
        if user_signing_certificates:
            for user_signing_certificate in user_signing_certificates:
                iam_client.delete_signing_certificate(
                    UserName=iam_user,
                    CertificateId=user_signing_certificate["CertificateId"],
                )
            logging.info(
                f"Deleted all signing certificates associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No signing certificates found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete signing certificates for user {iam_user}: {e}")
        exit(1)


def delete_user_public_ssh_keys(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for public SSH keys associated with {iam_user} in AWS account: {aws_account}"
        )
        public_ssh_keys = iam_client.list_ssh_public_keys(UserName=iam_user)
        user_public_ssh_keys = public_ssh_keys["SSHPublicKeys"]
        if user_public_ssh_keys:
            for user_public_ssh_key in user_public_ssh_keys:
                iam_client.delete_ssh_public_key(
                    UserName=iam_user,
                    SSHPublicKeyId=user_public_ssh_key["SSHPublicKeyId"],
                )
            logging.info(
                f"Deleted all public SSH keys associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No public SSH keys found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete public SSH keys for user {iam_user}: {e}")
        exit(1)


def delete_user_service_specific_credentials(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for service specific credentials associated with {iam_user} in AWS account: {aws_account}"
        )
        service_specific_credentials = iam_client.list_service_specific_credentials(
            UserName=iam_user
        )
        user_service_specific_credentials = service_specific_credentials[
            "ServiceSpecificCredentials"
        ]
        if user_service_specific_credentials:
            for user_service_specific_credential in user_service_specific_credentials:
                iam_client.delete_service_specific_credential(
                    UserName=iam_user,
                    ServiceSpecificCredentialId=user_service_specific_credential[
                        "ServiceSpecificCredentialId"
                    ],
                )
            logging.info(
                f"Deleted all service specific credentials associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No service specific credentials found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(
            f"Unable to delete service specific credentials for user {iam_user}: {e}"
        )
        exit(1)


def delete_user_mfa_device(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for MFA Devices associated with {iam_user} in AWS account: {aws_account}"
        )
        mfa_devices = iam_client.list_mfa_devices(UserName=iam_user)
        user_mfa_devices = mfa_devices["MFADevices"]
        if user_mfa_devices:
            for user_mfa_device in user_mfa_devices:
                iam_client.deactivate_mfa_device(
                    UserName=iam_user, SerialNumber=user_mfa_device["SerialNumber"]
                )
                iam_client.delete_virtual_mfa_device(
                    SerialNumber=user_mfa_device["SerialNumber"]
                )
            logging.info(
                f"Deleted MFA Devices associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No MFA Devices found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete MFA Devices for user {iam_user}: {e}")
        exit(1)


def delete_user_policies(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for policies associated with {iam_user} in AWS account: {aws_account}"
        )
        policies = iam_client.list_user_policies(UserName=iam_user)
        user_policies = policies["PolicyNames"]
        if user_policies:
            for user_policy in user_policies:
                iam_client.delete_user_policy(UserName=iam_user, PolicyName=user_policy)
            logging.info(
                f"Deleted all policies associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No policies found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete policies for user {iam_user}: {e}")
        exit(1)


def delete_attached_user_policies(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for attached policies associated with {iam_user} in AWS account: {aws_account}"
        )
        attached_policies = iam_client.list_attached_user_policies(UserName=iam_user)
        user_attached_policies = attached_policies["AttachedPolicies"]
        if user_attached_policies:
            for user_attached_policy in user_attached_policies:
                iam_client.detach_user_policy(
                    UserName=iam_user, PolicyArn=user_attached_policy["PolicyArn"]
                )
            logging.info(
                f"Deleted all attached policies associated with user {iam_user} in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No attached policies found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable to delete attached policies for user {iam_user}: {e}")
        exit(1)


def delete_user_from_groups(aws_account, iam_client, iam_user):
    try:
        logging.info(
            f"Checking for groups associated with {iam_user} in AWS account: {aws_account}"
        )
        groups = iam_client.list_groups_for_user(UserName=iam_user)
        user_groups = groups["Groups"]
        if user_groups:
            for user_group in user_groups:
                iam_client.remove_user_from_group(
                    UserName=iam_user, GroupName=user_group["GroupName"]
                )
            logging.info(
                f"Removed user {iam_user} from all groups in AWS account {aws_account}"
            )
        else:
            logging.info(
                f"No groups found to be associated with user {iam_user} in AWS account {aws_account}"
            )
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable remove user {iam_user} from groups: {e}")
        exit(1)


def delete_iam_user_account(aws_account, iam_client, iam_user):
    try:
        logging.info(f"Deleting IAM user {iam_user} in AWS account: {aws_account}")
        iam_client.delete_user(UserName=iam_user)
        logging.info(f"Deleted IAM user {iam_user} from {aws_account}")
    except botocore.exceptions.ClientError as e:
        logging.error(f"Unable remove user {iam_user} from {aws_account}: {e}")


def delete_iam_user_handler(aws_account, iam_client, iam_user):
    user_exists = check_if_user_exists(aws_account, iam_client, iam_user)
    if user_exists:
        delete_iam_login_profile(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_access_keys(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_signing_certificates(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_public_ssh_keys(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_service_specific_credentials(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_policies(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_mfa_device(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_attached_user_policies(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_user_from_groups(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        delete_iam_user_account(
            aws_account=aws_account, iam_client=iam_client, iam_user=iam_user
        )
        return True
    else:
        logging.info(f"Could not find user {iam_user} in {aws_account}, continuing")
        return False
