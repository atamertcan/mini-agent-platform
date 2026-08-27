from sqlalchemy.orm import Session
from app.core.agent_service import get_agent
from app.models import Tool
from app.schemas import ToolCreateRequest, ToolUpdateRequest


class ToolNotFoundError(Exception):
    pass

def create_tool(db: Session, tenant_id: int, agent_id: int, data: ToolCreateRequest) -> Tool:
    get_agent(db, tenant_id, agent_id)
    tool = Tool(tenant_id=tenant_id,agent_id=agent_id,name=data.name,description=data.description,url=data.url,http_method=data.http_method,
                parameters=[p.model_dump() for p in data.parameters])
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool

def list_tools(db: Session, tenant_id: int, agent_id: int) -> list[Tool]:
    get_agent(db, tenant_id, agent_id)
    return db.query(Tool).filter(Tool.tenant_id == tenant_id, Tool.agent_id == agent_id).all()

def get_tool(db: Session, tenant_id: int, agent_id: int, tool_id: int) -> Tool:
    tool = (db.query(Tool).filter(Tool.id == tool_id, Tool.tenant_id == tenant_id, Tool.agent_id == agent_id).first())
    if tool is None:
        raise ToolNotFoundError(tool_id)
    return tool

def update_tool(db: Session, tenant_id: int, agent_id: int, tool_id: int, data: ToolUpdateRequest) -> Tool:
    tool = get_tool(db, tenant_id, agent_id, tool_id)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if value is not None:
            setattr(tool, field, value)
    db.commit()
    db.refresh(tool)
    return tool

def delete_tool(db: Session, tenant_id: int, agent_id: int, tool_id: int) -> None:
    tool = get_tool(db, tenant_id, agent_id, tool_id)
    db.delete(tool)
    db.commit()
