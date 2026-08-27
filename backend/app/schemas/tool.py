from pydantic import BaseModel, ConfigDict


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str = ""
    required: bool = True

class ToolCreateRequest(BaseModel):
    name: str
    description: str
    url: str
    http_method: str = "POST"
    parameters: list[ToolParameter] = []

class ToolUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    url: str | None = None
    http_method: str | None = None
    parameters: list[ToolParameter] | None = None

class ToolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    url: str
    http_method: str
    parameters: list[ToolParameter]
