# This is just a protype not intended for use was just validating the concept

from langflow.custom import Component
from langflow.schema import Data
from langflow.io import MessageTextInput, Output
from loguru import logger
import hvac  # Hashicorp Vault Python client

class VaultSecretRetriever(Component):
    display_name = "Hashicorp Vault Secret Retriever"
    description = "Securely retrieves secrets from Hashicorp Vault"
    documentation: str = "https://www.vaultproject.io/docs"
    icon = "vault"
    name = "VaultSecretRetriever"

    inputs = [
        MessageTextInput(
            name="vault_url",
            display_name="Vault URL",
            info="URL of your Hashicorp Vault instance",
            value="http://localhost:8200",
            tool_mode=True,
        ),
        MessageTextInput(
            name="vault_role_id",
            display_name="Vault Role ID",
            info="Role ID for Vault AppRole authentication",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="vault_secret_id",
            display_name="Vault Secret ID",
            info="Secret ID for Vault AppRole authentication",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="secret_path",
            display_name="Secret Path",
            info="Path to the secret in Vault",
            value="secret/data/my-secret",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Secret Value", name="secret_value", method="get_secret"),
    ]

    def get_secret(self) -> Message:
        try:
            # Initialize the Vault client
            client = hvac.Client(url=self.vault_url)
            
            # Authenticate using AppRole
            client.auth.approle.login(
                role_id=self.vault_role_id,
                secret_id=self.vault_secret_id
            )
            
            # Retrieve the secret
            secret = client.secrets.kv.v2.read_secret_version(path=self.secret_path)
            
            # Extract the secret value
            secret_value = secret['data']['data']
            
            # Log success
            self.log("Successfully retrieved secret from Vault", "vault")
            logger.info(f"Secret retrieved from Vault: {self.secret_path}")
            
            return Message(value=secret_value)
            
        except Exception as e:
            error_message = f"Error retrieving secret from Vault: {str(e)}"
            self.log(error_message, "vault")
            logger.error(error_message)
            return Message(error=error_message)