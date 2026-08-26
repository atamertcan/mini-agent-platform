from pydantic import BaseModel, ConfigDict

class AgentCreateRequest(BaseModel):
    name: str
    system_prompt: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7

class AgentUpdateRequest(BaseModel):
    name: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = None

class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    system_prompt: str
    model: str
    temperature: float
