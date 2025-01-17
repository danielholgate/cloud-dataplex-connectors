"""A module to get a password from the Secret Manager."""
from google.cloud import secretmanager


def get_password(secret_path: str) -> str:
    """Gets password from a GCP service."""
    client = secretmanager.SecretManagerServiceClient()
    if "versions" not in secret_path:
