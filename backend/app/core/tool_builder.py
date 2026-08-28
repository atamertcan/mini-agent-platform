import requests
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, create_model
from app.models import Tool

TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}

def build_args_schema(tool: Tool) -> type[BaseModel]:
    fields = {}
    for param in tool.parameters:
        python_type = TYPE_MAP.get(param["type"], str)
        description = param.get("description", "")
        if param.get("required", True):
            fields[param["name"]] = (python_type, Field(..., description=description))
        else:
            fields[param["name"]] = (python_type | None, Field(None, description=description))
    return create_model(f"{tool.name}_args", **fields)

def build_tool_function(tool: Tool):
    def call_tool(**kwargs) -> str:
        url = tool.url.format(**kwargs)
        response = requests.request(tool.http_method, url, json=kwargs, headers=tool.headers, timeout=10)
        response.raise_for_status()
        return response.text

    return call_tool

def build_structured_tool(tool: Tool) -> StructuredTool:
    return StructuredTool.from_function(
        func=build_tool_function(tool),
        name=tool.name,
        description=tool.description,
        args_schema=build_args_schema(tool),
    )
