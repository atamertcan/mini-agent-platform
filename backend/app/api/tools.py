from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.agent_service import AgentNotFoundError
from app.core.tool_service import (
    ToolNotFoundError,
    create_tool,
    delete_tool,
    get_tool,
    list_tools,
    update_tool,
)
from app.db.session import get_db
from app.models import User
from app.schemas import ToolCreateRequest, ToolResponse, ToolUpdateRequest

router = APIRouter(prefix="/agents/{agent_id}/tools", tags=["tools"])

@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
def create(agent_id: int,data: ToolCreateRequest,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        return create_tool(db, current_user.tenant_id, agent_id, data)
    except AgentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

@router.get("/", response_model=list[ToolResponse])
def list_all(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return list_tools(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

@router.get("/{tool_id}", response_model=ToolResponse)
def get_one(agent_id: int,tool_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        return get_tool(db, current_user.tenant_id, agent_id, tool_id)
    except ToolNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

@router.patch("/{tool_id}", response_model=ToolResponse)
def update(agent_id: int,tool_id: int,data: ToolUpdateRequest,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        return update_tool(db, current_user.tenant_id, agent_id, tool_id, data)
    except ToolNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(agent_id: int,tool_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        delete_tool(db, current_user.tenant_id, agent_id, tool_id)
    except ToolNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
