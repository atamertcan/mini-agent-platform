from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from sqlalchemy.orm import Session
from app.core.agent_service import get_agent
from app.core.llm import get_llm
from app.core.tool_builder import build_structured_tool
from app.models import Conversation, Message

MAX_TOOL_TURNS = 5

class ConversationNotFoundError(Exception):
    pass

def get_conversation(db: Session, tenant_id: int, conversation_id: int) -> Conversation:
    conversation = (db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.tenant_id == tenant_id).first())
    if conversation is None:
        raise ConversationNotFoundError(conversation_id)
    return conversation

def send_message(db: Session,tenant_id: int,agent_id: int,content: str,conversation_id: int | None = None) -> Message:
    agent = get_agent(db, tenant_id, agent_id)
    tools = [build_structured_tool(tool) for tool in agent.tools]
    tools_by_name = {tool.name: tool for tool in tools}

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
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))
    history.append(HumanMessage(content=content))

    llm = get_llm(agent)
    llm_to_call = llm.bind_tools(tools) if tools else llm

    tool_records = []
    response = llm_to_call.invoke(history)
    turns = 0
    while response.tool_calls and turns < MAX_TOOL_TURNS:
        history.append(response)
        for call in response.tool_calls:
            tool = tools_by_name.get(call["name"])
            if tool is None:
                result_text = f"Tool '{call['name']}' bulunamadı."
            else:
                try:
                    result_text = tool.invoke(call["args"])
                except Exception as exc:
                    result_text = f"Tool çalışırken hata olustu: {exc}"
            history.append(ToolMessage(content=result_text, tool_call_id=call["id"]))
            tool_records.append((call["name"], call["args"], result_text))
        turns += 1
        response = llm_to_call.invoke(history)

    final_content = response.content or "İşlemi tamamlayamadım, tekrar dener misin?"

    db.add(Message(conversation_id=conversation.id, role="user", content=content))
    for name, args, result_text in tool_records:
        db.add(Message(conversation_id=conversation.id,role="tool",content=f"{name}({args}) -> {result_text}",))
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=final_content)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return assistant_message
