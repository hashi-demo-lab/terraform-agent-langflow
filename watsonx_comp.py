from typing import Any, Dict
from langflow.custom import Component
from langflow.io import MultilineInput, SecretStrInput, DropdownInput, Output, BoolInput
from langflow.schema import Data
from langflow.field_typing import LanguageModel
from langflow.schema.message import Message

# Make sure these IBM libraries are installed
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import Model
except ImportError:
    raise ImportError(
        "IBM Watson libraries not found. Please install them with: pip install ibm-watson-watsonx-ai"
    )

class WatsonxComponent(Component):
    """
    A Langflow component for IBM watsonx.ai integration.
    """
    display_name = "IBM watsonx.ai"
    description = "Connect to IBM watsonx.ai for AI model inference"
    icon = "custom_components"
    documentation = "https://cloud.ibm.com/apidocs/watsonx"
    name = "WatsonxComponent"
    
    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="IBM Cloud API Key",
            required=True,
        ),
        SecretStrInput(
            name="endpoint",
            display_name="Endpoint URL",
            info="Region endpoint URL for IBM watsonx.ai",
            required=True,
            value="https://us-south.ml.cloud.ibm.com"
        ),
        MultilineInput(
            name="prompt",
            display_name="Prompt",
            info="Input text",
            required=True,
        ),
        DropdownInput(
            name="model_id",
            display_name="Model ID",
            options=[
                "ibm/granite-13b-chat-v2",
                "ibm/granite-20b-code-instruct-v1",
                "meta-llama/llama-2-70b-chat",
            ],
            value="ibm/granite-13b-chat-v2",
            info="Select the watsonx.ai model to use",
            required=True,
        ),
        DropdownInput(
            name="temperature",
            display_name="Temperature",
            options=["0.5", "0.7", "0.9"],
            value="0.7",
            info="Controls randomness",
            required=False,
        ),
        DropdownInput(
            name="max_tokens",
            display_name="Max Tokens",
            options=["512", "1024", "2048"],
            value="1024",
            info="Maximum tokens to generate",
            required=False,
        ),
        BoolInput(
            name="enable_tools",
            display_name="Enable Tool Models",
            info="Toggle to enable additional tool support",
            value=False,
            required=False
        ),
    ]
    
    outputs = [
        Output(
            name="language_model",
            display_name="Language Model",
            info="Callable tool for IBM watsonx.ai model",
            method="build_model",
        ),
        Output(
            name="message",
            display_name="Message",
            info="Generated text as a Message",
            method="build_message",
        ),
    ]
    
    def build_model(self) -> LanguageModel:
        """
        Build a callable tool (LanguageModel) for IBM watsonx.ai.
        """
        def tool(prompt: str, temperature: float = None, max_tokens: int = None) -> str:
            try:
                t = float(temperature) if temperature is not None else float(self.temperature) if self.temperature else 0.7
                tokens = int(max_tokens) if max_tokens is not None else int(self.max_tokens) if self.max_tokens else 1024
                api_key = self.api_key.get_secret_value() if hasattr(self.api_key, "get_secret_value") else self.api_key
                endpoint = self.endpoint.get_secret_value() if hasattr(self.endpoint, "get_secret_value") else self.endpoint
                credentials = Credentials(url=endpoint, api_key=api_key)
                client = APIClient(credentials)
                model_id = self.model_id
                model_params = {
                    "max_new_tokens": tokens,
                    "temperature": t,
                }
                model_instance = Model(model_id=model_id, params=model_params, client=client)
                result = model_instance.generate(inputs=prompt)
                return result.generated_text
            except Exception as e:
                return f"Error: {str(e)}"
        return tool
    
    def build_message(self) -> Message:
        """
        Build the component output as a Message object.
        """
        try:
            api_key = self.api_key.get_secret_value() if hasattr(self.api_key, "get_secret_value") else self.api_key
            endpoint = self.endpoint.get_secret_value() if hasattr(self.endpoint, "get_secret_value") else self.endpoint
            credentials = Credentials(url=endpoint, api_key=api_key)
            client = APIClient(credentials)
            model_id = self.model_id
            prompt = self.prompt
            t = float(self.temperature) if self.temperature else 0.7
            tokens = int(self.max_tokens) if self.max_tokens else 1024
            model_params = {
                "max_new_tokens": tokens,
                "temperature": t,
            }
            model_instance = Model(model_id=model_id, params=model_params, client=client)
            result = model_instance.generate(inputs=prompt)

            return Message(text=result.generated_text)
        except Exception as e:
            return Message(text=f"Error: {str(e)}")
