from typing import Any, Dict
from langflow.custom import Component
from langflow.io import MultilineInput, MessageTextInput, SecretStrInput, DropdownInput, Output, BoolInput, SliderInput
from langflow.schema import Data
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.schema.message import Message
from ibm_watsonx_ai import APIClient, Credentials
from langchain_ibm import ChatWatsonx

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
        MessageTextInput(
            name="endpoint",
            display_name="Endpoint URL",
            info="Region endpoint URL for IBM watsonx.ai",
            required=True,
            value="https://us-south.ml.cloud.ibm.com"
        ),
        MessageTextInput(
            name="project_id",
            display_name="Project ID",
            info="IBM Watsonx.ai Project ID",
            required=True,
            value="76673d5e-76e3-428c-9134-f8975dead5d4"
        ),
        MultilineInput(
            name="prompt",
            display_name="Prompt",
            info="Input text",
            required=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            info="Input text",
            required=True,
            value="You are a helpful assistant."
        ),
        DropdownInput(
            name="model_id",
            display_name="Model ID",
            options=[
                "ibm/granite-3-2-8b-instruct",
                "meta-llama/llama-3-3-70b-instruct",
                "mistralai/mistral-large"
            ],
            value="ibm/granite-3-2-8b-instruct",
            info="Select the watsonx.ai model to use",
            required=True,
        ),
        DropdownInput(
            name="max_tokens",
            display_name="Max Tokens",
            options=["512", "1024", "2048", "4096"],
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
        )
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
            api_key = self.api_key
            endpoint = self.endpoint
            model_id = self.model_id
            model_params = {
                "max_new_tokens": tokens,
                "time_limit": 1000,
            }

            # Create credentials and API client, then set the default project
            credentials = Credentials(api_key=api_key, url=endpoint)
            client = APIClient(credentials)
            client.set.default_project(self.project_id)

            output = ChatWatsonx(
                model_id=model_id,
                watsonx_client=client, 
                params=model_params,
                project_id=self.project_id,
                url=endpoint
            )

            return output

    def build_message(self) -> Message:
        """
        Build the component output as a Message object.
        Always streams the output.
        """
        try:
            # Properly extract secret values
            api_key = self.api_key
            endpoint = self.endpoint

            # Create credentials and API client, then set the default project
            credentials = Credentials(api_key=api_key, url=endpoint)
            client = APIClient(credentials)
            client.set.default_project(self.project_id)

            model_id = self.model_id
            prompt = self.prompt

            tokens = int(self.max_tokens) if self.max_tokens else 1024

            model_params = {
                "max_new_tokens": tokens,
                "time_limit": 1000,
            }
            verify = False

            # Instantiate the Model with credentials
            model = ChatWatsonx(
                model_id=model_id,
                watsonx_client=client,  # Fixed: api_client -> client
                params=model_params,
                project_id=self.project_id,
                url=endpoint,  # Added url parameter
                verify=verify,
            )

            # Use the correct method for sending messages
            prompt_formatted = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Use proper invoke method and access response correctly
            result = model.invoke(prompt_formatted)  # Fixed: chat -> invoke
            
            return Message(text=result.content)  # Fixed: accessing content from response object
        except Exception as e:
            return Message(text=f"Error: {str(e)}")  # Fixed: proper string conversion for exception
