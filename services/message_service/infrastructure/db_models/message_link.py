# TODO: Описать таблицу message_links для references.
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from libs.postgres.base import Base


class MessageLinkModel(Base):
    __tablename__ = "references"
    target_id = Column(UUID(as_uuid=True), ForeignKey("message.id", ondelete="CASCADE"), primary_key=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("message.id", ondelete="CASCADE"), primary_key=True)
