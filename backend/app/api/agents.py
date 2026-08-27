from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.agent_service import (
    AgentNotFoundError,
    create_agent,
    delete_agent,
    get_agent,
    list_agents,
    update_agent,
)
from app.core.chat_service import ConversationNotFoundError, send_message
from app.db.session import get_db
from app.models import User
from app.schemas import AgentCreateRequest, AgentResponse, AgentUpdateRequest, ChatRequest, ChatResponse

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create(data: AgentCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_agent(db, current_user.tenant_id, data)

@router.get("/", response_model=list[AgentResponse])
def list_all(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    return list_agents(db, current_user.tenant_id)

@router.get("/{agent_id}", response_model=AgentResponse)
def get_one(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return get_agent(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

@router.patch("/{agent_id}", response_model=AgentResponse)
def update(agent_id: int, data: AgentUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return update_agent(db, current_user.tenant_id, agent_id, data)
    except AgentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        delete_agent(db, current_user.tenant_id, agent_id)
    except AgentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

@router.post("/{agent_id}/chat", response_model=ChatResponse)
def chat(agent_id: int, data: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return send_message(db, current_user.tenant_id, agent_id, data.content, data.conversation_id)
    except AgentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
