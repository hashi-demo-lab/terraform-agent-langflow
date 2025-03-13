from typing import Dict, Any
from langflow.custom import Component  # Fixed incorrect import
from langflow.schema import Data  # Fixed missing import
from langflow.custom.constants import ComponentCategory
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models import Model
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

class WatsonxComponent(Component):
    """
    A simplified Langflow component for IBM watsonx integration.
    """
    
    display_name: str = "IBM watsonx"
    description: str = "Connect to IBM watsonx for AI model inference"
    category: str = "LLM"
    
    def build_config(self):
        """Define the configuration parameters for the component."""
        return {
            "api_key": {
                "display_name": "API Key",
                "description": "IBM Cloud API Key",
                "type": "str",
                "required": True,
                "password": True,
            },
            "project_id": {
                "display_name": "Project ID",
                "description": "IBM watsonx Project ID",
                "type": "str", 
                "required": True,
            },
            "model_id": {
                "display_name": "Model ID",
                "description": "watsonx model to use",
                "type": "str",
                "required": True,
                "options": [
                    "ibm/granite-13b-chat-v2",
                    "ibm/granite-20b-code-instruct-v1",
                    "meta-llama/llama-2-70b-chat"
                ],
                "default": "ibm/granite-13b-chat-v2",
            },
            "prompt": {
                "display_name": "Prompt",
                "description": "Input text",
                "type": "str",
                "required": True,
            },
            "temperature": {
                "display_name": "Temperature",
                "description": "Controls randomness",
                "type": "float",
                "required": False,
                "default": 0.7,
            },
            "max_tokens": {
                "display_name": "Max Tokens",
                "description": "Maximum tokens to generate",
                "type": "int",
                "required": False,
                "default": 1024,
            }
        }
    
    def build(
        self,
        api_key: str,
        project_id: str,
        model_id: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build the component with minimal configuration.
        """
        try:
            # Set up authentication and client
            authenticator = IAMAuthenticator(api_key)
            client = APIClient(authenticator=authenticator)
            client.set_default_project(project_id)
            
            # Configure the model with basic parameters
            params = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # Initialize model and generate text
            model = Model(model_id=model_id, params=params, client=client)
            result = model.generate(inputs=prompt)  # Fixed incorrect parameter name
            
            # Return a simple response structure
            return {
                "response": result.generated_text,
                "model_id": model_id
            }
            
        except Exception as e:
            return {"error": str(e)}
