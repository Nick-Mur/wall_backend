# TODO: Описать таблицы жалоб, если модуль report остаётся в scope.
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from libs.postgres.base import Base
from datetime import datetime
import uuid

class ReportModel(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
