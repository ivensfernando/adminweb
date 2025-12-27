import boto3
import botocore
import traceback

from config.settings.base import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_ENDPOINT_URL, AWS_S3_REGION_NAME, \
    AWS_STORAGE_BUCKET_NAME

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=AWS_S3_ENDPOINT_URL,
    region_name=AWS_S3_REGION_NAME,
    verify=True  # Consider this only if you have SSL issues, but be aware of the security implications
)


def save_s3(
        key: str,
        company_id: str,
        value,
):
    try:
        value.seek(0)  # Reset buffer position
        path = f"{AWS_STORAGE_BUCKET_NAME}_{company_id}"
        response = s3_client.upload_fileobj(value, path, key)
        print(f"save_s3, response={response}")
        s3_url = f"{path}/{key}"

        return s3_url
    except botocore.exceptions.ClientError as e:
        traceback.print_exc()
        # Specific exception handling for boto3's client errors
        print(f"save_s3, Encountered an error ClientError, with boto3: {e}")
        return ""
    except Exception as e:
        traceback.print_exc()
        print(f"save_s3, Encountered an error Exception, with boto3: {e}")
        return ""
