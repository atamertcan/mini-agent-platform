import logging

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.cache import cache_delete, cache_get, cache_set
from app.core.snapshots import AgentSnapshot
from app.models import Agent
from app.schemas import AgentCreateRequest, AgentUpdateRequest

logger = logging.getLogger(__name__)

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

def agent_cache_key(tenant_id: int, agent_id: int) -> str:
    return f"agent:v1:{tenant_id}:{agent_id}"

def invalidate_agent_cache(tenant_id: int, agent_id: int) -> None:
    cache_delete(agent_cache_key(tenant_id, agent_id))

def get_agent_snapshot(db: Session, tenant_id: int, agent_id: int) -> AgentSnapshot:
    key = agent_cache_key(tenant_id, agent_id)

    cached = cache_get(key)
    if cached is not None:
        try:
            snapshot = AgentSnapshot.model_validate_json(cached)
            logger.info("agent cache hit: %s", key)
            return snapshot
        except ValidationError:
            logger.warning("agent cache entry is invalid, refetching: %s", key)

    logger.info("agent cache miss: %s", key)
    agent = get_agent(db, tenant_id, agent_id)
    snapshot = AgentSnapshot.model_validate(agent)
    cache_set(key, snapshot.model_dump_json(), get_settings().agent_cache_ttl_seconds)
    return snapshot

def update_agent(db: Session, tenant_id: int, agent_id: int, data: AgentUpdateRequest) -> Agent:
    agent = get_agent(db, tenant_id, agent_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if value is not None:
            setattr(agent, key, value)
    db.commit()
    invalidate_agent_cache(tenant_id, agent_id)
    db.refresh(agent)
    return agent

def delete_agent(db: Session, tenant_id: int, agent_id: int) -> None:
    agent = get_agent(db, tenant_id, agent_id)
    db.delete(agent)
    db.commit()
    invalidate_agent_cache(tenant_id, agent_id)
