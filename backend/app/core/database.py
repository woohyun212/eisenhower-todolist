"""DynamoDB resource factory for sync boto3 client."""

import boto3

from app.core.config import settings


def get_dynamodb_resource():
    """Create and return a boto3 DynamoDB resource (sync)."""
    kwargs = {
        "region_name": settings.AWS_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }
    # Only set endpoint_url for local DynamoDB (testing)
    if settings.DYNAMODB_ENDPOINT_URL and "localhost" in settings.DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def get_dynamodb_table(table_name: str = None):
    """Get a specific DynamoDB table resource."""
    if table_name is None:
        table_name = settings.DYNAMODB_TABLE_NAME
    resource = get_dynamodb_resource()
    return resource.Table(table_name)
