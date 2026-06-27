from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from libs.postgres.base import Base


class SearchLogModel(Base):
    __tablename__ = "search_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    query_string = Column(String, nullable=False)
    results_count = Column(Integer, nullable=False, default=0)
