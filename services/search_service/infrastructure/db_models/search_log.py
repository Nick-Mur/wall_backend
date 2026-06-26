from libs.postgres.base import Base
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID


class SearchLogModel(Base):
    __tablename__ = "search_log"
    id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    search_request = Column(String, nullable=False)
