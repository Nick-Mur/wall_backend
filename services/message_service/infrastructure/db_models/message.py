# TODO: Описать таблицу messages.
from libs.postgres.base import Base
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class MessageModel(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True)
    text = Column(String(), nullable=False)
    hidden = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=True)
    hashes = relationship("MessageHashModel", back_populates="message", cascade="all, delete-orphan")
    moderation_logs = relationship("ModerationLogModel", back_populates="message")
