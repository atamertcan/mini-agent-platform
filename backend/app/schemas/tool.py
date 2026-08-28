from pydantic import BaseModel, ConfigDict, Field

# LLM saglayicilarinin cogu (Anthropic, Google, Bedrock) tool/fonksiyon
# isminde bosluk veya unicode karakter kabul etmiyor.
NAME_PATTERN = r"^[a-zA-Z0-9_-]{1,128}$"

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str = ""
    required: bool = True

class ToolCreateRequest(BaseModel):
    name: str = Field(pattern=NAME_PATTERN)
    description: str
    url: str
    http_method: str = "POST"
    parameters: list[ToolParameter] = []
    headers: dict[str, str] = {}

class ToolUpdateRequest(BaseModel):
    name: str | None = Field(default=None, pattern=NAME_PATTERN)
    description: str | None = None
    url: str | None = None
    http_method: str | None = None
    parameters: list[ToolParameter] | None = None
    headers: dict[str, str] | None = None

class ToolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    url: str
    http_method: str
    parameters: list[ToolParameter]
    headers: dict[str, str]
