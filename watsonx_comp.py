from typing import Any, Dict
from langflow.custom import Component
from langflow.io import MultilineInput, MessageTextInput, SecretStrInput, DropdownInput, Output, BoolInput, SliderInput
from langflow.schema import Data
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.schema.message import Message
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
#IBM Watson libraries not found. Please install them with: pip install ibm-watson-watsonx-ai

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
        DropdownInput(
            name="model_id",
            display_name="Model ID",
            options=[
                "ibm/granite-3-2-8b-instruct",
                "meta-llama/llama-3-3-70b-instruct",
                "ibm/granite-34b-code-instruct"
            ],
            value="ibm/granite-13b-chat-v2",
            info="Select the watsonx.ai model to use",
            required=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.1,
            info="Run inference with this temperature. Must be in the closed interval [0.0, 1.0].",
            range_spec=RangeSpec(min=0, max=1, step=0.01),
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
        Always streams the output.
        """
        def tool(prompt: str, temperature: float = None, max_tokens: int = None) -> str:
            try:
                t = float(temperature) if temperature is not None else (float(self.temperature) if self.temperature else 0.7)
                tokens = int(max_tokens) if max_tokens is not None else (int(self.max_tokens) if self.max_tokens else 1024)
                
                # Properly extract secret values
                api_key = self.api_key
                endpoint = self.endpoint
                
                # Create credentials and API client, then set the default project
                credentials = Credentials(api_key=api_key, url=endpoint)

                
                # Create client with credentials
                client = APIClient(credentials)
                client.set.default_project(self.project_id)
                
                model_id = self.model_id
                model_params = {
                    "max_new_tokens": tokens,
                    "time_limit": 1000,
                }
                verify = False
                
                # Instantiate the ModelInference with credentials
                model = ModelInference(
                    model_id=model_id,
                    api_client=client,
                    params=model_params,
                    project_id=self.project_id,
                    verify=verify,
                )
                
                # Always use streaming.
                final_text = ""
                result_iter = model.chat(messages=prompt, stream=True)
                for chunk in result_iter:
                    final_text += chunk.generated_text
                return final_text
            except Exception as e:
                return f"Error: {str(e)}"
        return tool
    
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
            t = float(self.temperature) if self.temperature else 0.7
            tokens = int(self.max_tokens) if self.max_tokens else 1024
            
            model_params = {
                "max_new_tokens": tokens,
                "time_limit": 1000,
            }
            verify = False
            
            # Instantiate the Model with credentials
            model = ModelInference(
                model_id=model_id,
                api_client=client,
                params=model_params,
                project_id=self.project_id,
                verify=verify,
            )
            
            # Always use streaming.
            final_text = ""
            result_iter = model.chat(messages=prompt, stream=True)
            for chunk in result_iter:
                final_text += chunk.generated_text
            return Message(text=final_text)
        except Exception as e:
            return Message(text=f"Error: {str(e)}")