"""Azure Key Vault secrets module."""

import os

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

from dul.common.exceptions import MissingEnvVar


class Secrets(dict):
    """Azure Key Vault secrets reader.

    The following environment variables MUST be set:\n
    APPLICATION_ID - Service principal app ID\n
    APPLICATION_SECRET - Service principal app password\n
    TENANT_ID - Azure subscription ID\n

    Args:
        key_vault (str): Key Vault name

    Returns:
        dict[str, str]: Dictionary of secret keys to secret values

    Raises:
        MissingEnvVar
    """

    def __init__(self, key_vault: str, *args, **kwargs) -> dict[str, str]:
        dict.__init__(self, *args, **kwargs)
        self.vault_url = f"https://{key_vault}.vault.azure.net"
        app_id = os.getenv("APPLICATION_ID")
        if app_id is None:
            raise MissingEnvVar("APPLICATION_ID")
        app_secret = os.getenv("APPLICATION_SECRET")
        if app_secret is None:
            raise MissingEnvVar("APPLICATION_SECRET")
        tenant_id = os.getenv("TENANT_ID")
        if tenant_id is None:
            raise MissingEnvVar("TENANT_ID")
        self.credential = ClientSecretCredential(tenant_id, app_id, app_secret)

    def init(self):
        """Initialize the secrets reader."""

        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    def terminate(self):
        """Terminate the secrets reader."""

        self.clear()
        self.client.close()

    def __enter__(self):
        self.init()

    def __exit__(self):
        self.terminate()

    def __getitem__(self, key: str):
        if key not in self:
            try:
                secret = self.client.get_secret(key)
                self[key] = secret.value
            except ResourceNotFoundError:
                return None
        return self[key]
