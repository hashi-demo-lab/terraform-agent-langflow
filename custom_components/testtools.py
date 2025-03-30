# Standard library imports
from collections.abc import Sequence
from typing import Any

# Third-party imports
from composio.client.collections import AppAuthScheme
from composio.client.exceptions import NoItemsFound
from composio_langchain import Action, App, ComposioToolSet, WorkspaceType
from langchain_core.tools import Tool
from loguru import logger

# from langflow.field_typing import Data
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data


class CustomComponent(Component):
    display_name = "Custom Component"
    description = "Use as a template to create your own component."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "code"
    name = "CustomComponent"

    inputs = [
        MessageTextInput(
            name="input_value",
            display_name="Input Value",
            info="This is a custom component Input",
            value="Hello, World!",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
        Output(name="code_tools", display_name="Code_Tools", method="code_tool"),
        Output(name="file_tools", display_name="File_Tools", method="file_tool"),
    ]

    def build_output(self) -> Data:
        data = Data(value=self.input_value)
        self.status = data
        return data
    
    
    composio_toolset = ComposioToolSet(
        workspace_config=WorkspaceType.Docker(),
        metadata={
            App.CODE_ANALYSIS_TOOL: {
                "dir_to_index_path": f"/home/user/{repo_name}",
            }
        },
        processors={
            "pre": {
                App.FILETOOL: pop_thought_from_request,
                App.CODE_ANALYSIS_TOOL: pop_thought_from_request,
                App.SHELLTOOL: pop_thought_from_request,
            },
            "schema": {
                App.FILETOOL: add_thought_to_request,
                App.CODE_ANALYSIS_TOOL: add_thought_to_request,
                App.SHELLTOOL: add_thought_to_request,
            },
        },
    )
    composio_toolset.set_workspace_id(workspace_id)

    swe_tools = [
        *composio_toolset.get_actions(
            actions=[
                # Action.FILETOOL_OPEN_FILE,
                Action.FILETOOL_GIT_REPO_TREE,
                Action.FILETOOL_GIT_PATCH,
            ]
        ),
    ]
    # Separate tools into two groups
    code_analysis_tools = [
        *composio_toolset.get_actions(
            actions=[
                Action.CODE_ANALYSIS_TOOL_GET_CLASS_INFO,
                Action.CODE_ANALYSIS_TOOL_GET_METHOD_BODY,
                Action.CODE_ANALYSIS_TOOL_GET_METHOD_SIGNATURE,
                # Action.CODE_ANALYSIS_TOOL_GET_RELEVANT_CODE
            ]
        ),
    ]
    file_tools = [
        *composio_toolset.get_actions(
            actions=[
                Action.FILETOOL_GIT_REPO_TREE,
                Action.FILETOOL_LIST_FILES,
                Action.FILETOOL_CHANGE_WORKING_DIRECTORY,
                Action.FILETOOL_OPEN_FILE,
                Action.FILETOOL_SCROLL,
                Action.FILETOOL_EDIT_FILE,
                Action.FILETOOL_CREATE_FILE,
                Action.FILETOOL_FIND_FILE,
                Action.FILETOOL_SEARCH_WORD,
                Action.FILETOOL_WRITE,
            ]
        ),
    ]