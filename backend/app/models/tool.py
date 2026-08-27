from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    http_method: Mapped[str] = mapped_column(String, nullable=False, default="POST")
    parameters: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    tenant: Mapped["Tenant"] = relationship(back_populates="tools")
    agent: Mapped["Agent"] = relationship(back_populates="tools")
