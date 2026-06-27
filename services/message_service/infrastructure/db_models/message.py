# TODO: Описать таблицу messages.
from libs.postgres.base import Base
from sqlalchemy import Column, DateTime, String, Boolean, Computed, Index
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import relationship


class MessageModel(Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_tsv", "tsv", postgresql_using="gin"),)

    id = Column(UUID(as_uuid=True), primary_key=True)
    text = Column(String(), nullable=False)
    tsv = Column(TSVECTOR, Computed("to_tsvector('simple', text)", persisted=True))
    hidden = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=True)
    hashes = relationship("MessageHashModel", back_populates="message", cascade="all, delete-orphan")
    moderation_logs = relationship("ModerationLogModel", back_populates="message")


# Register related mapped classes used by string-based relationships above.
from services.message_service.infrastructure.db_models.message_hash import MessageHashModel  # noqa: E402,F401
from services.message_service.infrastructure.db_models.moderation_log import ModerationLogModel  # noqa: E402,F401
