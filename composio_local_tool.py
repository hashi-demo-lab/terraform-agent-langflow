# Standard library imports
from collections.abc import Sequence
from typing import Any

# Third-party imports
from composio.client.collections import AppAuthScheme
from composio.client.exceptions import NoItemsFound
from composio_langchain import Action, ComposioToolSet
from langchain_core.tools import Tool
from loguru import logger

# Local imports
from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.inputs import DropdownInput, LinkInput, MessageTextInput, MultiselectInput, SecretStrInput, StrInput
from langflow.io import Output


class ComposioAPIComponent(LCToolComponent):
    display_name: str = "Composio Local Tools"
    description: str = "Use Composio toolset to run actions with your agent"
    name = "ComposioAPI"
    icon = "Composio"
    documentation: str = "https://docs.composio.dev"

    inputs = [
        DropdownInput(
            name="app_names",
            display_name="App Name",
            options=[],
            value="",
            info="The app name to use. Please refresh after selecting app name",
            refresh_button=True,
            required=True,
        )
    ]

    outputs = [
        Output(name="tools", display_name="Tools", method="build_tool"),
    ]

    def build_tool(self) -> Sequence[Tool]:
        """Build Composio tools based on selected actions.

        Returns:
            Sequence[Tool]: List of configured Composio tools.
        """
        composio_toolset = ComposioToolSet()
        return composio_toolset.get_tools(self.tool_names)

