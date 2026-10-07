from pydantic import BaseModel, ConfigDict


class ToolSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    url: str
    http_method: str
    parameters: list[dict]
    headers: dict[str, str]


class AgentSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    system_prompt: str
    model: str
    temperature: float
    tools: list[ToolSnapshot]
