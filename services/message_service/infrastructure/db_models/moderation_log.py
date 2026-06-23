# TODO: Описать таблицу moderation_log.
from libs.postgres.base import Base
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ModerationLogModel(Base):
    __tablename__ = "moderation_log"
    id = Column(UUID(as_uuid=True), primary_key=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("message.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verdict = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    message = relationship("MessageModel", back_populates="moderation_logs")
