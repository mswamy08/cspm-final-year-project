import boto3

def get_aws_session(region=None):
    """Returns a boto3 session (uses default credentials chain)."""
    return boto3.Session(region_name=region)
