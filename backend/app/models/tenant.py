from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    agents: Mapped[list["Agent"]] = relationship(back_populates="tenant")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="tenant")
    tools: Mapped[list["Tool"]] = relationship(back_populates="tenant")
