from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy.orm import Session
from app.core.agent_service import get_agent
from app.core.llm import get_llm
from app.models import Conversation, Message


class ConversationNotFoundError(Exception):
    pass

def get_conversation(db: Session, tenant_id: int, conversation_id: int) -> Conversation:
    conversation = (db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.tenant_id == tenant_id).first())
    if conversation is None:
        raise ConversationNotFoundError(conversation_id)
    return conversation

def send_message(db: Session, tenant_id: int, agent_id: int, content: str, conversation_id: int | None = None) -> Message:
    agent = get_agent(db, tenant_id, agent_id)

    if conversation_id is None:
        conversation = Conversation(tenant_id=tenant_id, agent_id=agent_id)
        db.add(conversation)
        db.flush()
        previous_messages = []
    else:
        conversation = get_conversation(db, tenant_id, conversation_id)
        previous_messages = conversation.messages

    history = [SystemMessage(content=agent.system_prompt)]
    for msg in previous_messages:
        history.append(
            HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)
        )
    history.append(HumanMessage(content=content))

    response = get_llm(agent).invoke(history)

    db.add(Message(conversation_id=conversation.id, role="user", content=content))
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=response.content)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return assistant_message
