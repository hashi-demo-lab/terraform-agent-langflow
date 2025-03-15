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
    display_name: str = "Composio Local Git and File Tools"
    description: str = "Use Composio toolset to run actions with your agent related to local Git and File operations."
    name = "ComposioAPI"
    icon = "Composio"
    documentation: str = "https://docs.composio.dev"

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="Composio API Key",
            required=True,
            info="Refer to https://docs.composio.dev/faq/api_key/api_key",
            real_time_refresh=True,
        ),
        DropdownInput(
            name="tool_actions",
            display_name="Tool Names",
            options=['FILETOOL_GIT_CLONE','FILETOOL_GIT_REPO_TREE','FILETOOL_GIT_CUSTOM','FILETOOL_LIST_FILES','FILETOOL_CREATE_FILE','FILETOOL_EDIT_FILE'],
            value="",
            info="The tool name to use. Please refresh after selecting app name",
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
        composio_toolset = ComposioToolSet(api_key=self.api_key)
        return composio_toolset.get_tools(actions=[self.tool_actions])

