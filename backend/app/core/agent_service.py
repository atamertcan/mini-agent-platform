from sqlalchemy.orm import Session
from app.models import Agent
from app.schemas import AgentCreateRequest, AgentUpdateRequest

class AgentNotFoundError(Exception):
    pass

def create_agent(db: Session, tenant_id: int, data: AgentCreateRequest) -> Agent:
    agent = Agent(
        tenant_id=tenant_id,
        name=data.name,
        system_prompt=data.system_prompt,
        model=data.model,
        temperature=data.temperature,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

def list_agents(db: Session, tenant_id: int) -> list[Agent]:
    return db.query(Agent).filter(Agent.tenant_id == tenant_id).all()

def get_agent(db: Session, tenant_id: int, agent_id: int) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.tenant_id == tenant_id).first()
    if agent is None:
        raise AgentNotFoundError(agent_id)
    return agent

def update_agent(db: Session, tenant_id: int, agent_id: int, data: AgentUpdateRequest) -> Agent:
    agent = get_agent(db, tenant_id, agent_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if value is not None:
            setattr(agent, key, value)
    db.commit()
    db.refresh(agent)
    return agent

def delete_agent(db: Session, tenant_id: int, agent_id: int) -> None:
    agent = get_agent(db, tenant_id, agent_id)
    db.delete(agent)
    db.commit()
