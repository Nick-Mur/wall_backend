# TODO: Описать таблицу message_hashes для защиты от дублей.
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from libs.postgres.base import Base


class MessageHashModel(Base):
    __tablename__ = "message_hashes"
    hash = Column(String(), primary_key=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("MessageModel", ondelete="CASCADE"), nullable=False)
    message = relationship("MessageModel", back_populates="hashes")
