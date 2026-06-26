import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

from services.message_service.infrastructure.repositories.message_repo import MessageRepository
from services.message_service.domain.message import Message

TestBase = declarative_base()


class TestMessageModel(TestBase):
    __tablename__ = 'messages'
    id = Column(UUID, primary_key=True)
    text = Column(String)
    author_id = Column(UUID)
    hidden = Column(Boolean)
    created_at = Column(DateTime)


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    return MessageRepository(mock_session)


@pytest.fixture
def sample_message():
    return Message(
        id=uuid4(),
        text="Test message",
        author_id=uuid4(),
        hidden=False,
        created_at=datetime.now(),
        references=[]
    )


@pytest.mark.asyncio
class TestMessageRepository:

    async def test_should_save_message(self, repository, mock_session, sample_message):
        """Saving message"""
        with patch('services.message_service.infrastructure.repositories.message_repo.MessageModel', TestMessageModel):
            # Act
            await repository.save(sample_message)

            # Assert
            mock_session.add.assert_called_once()
            called_model = mock_session.add.call_args[0][0]
            assert isinstance(called_model, TestMessageModel)
            assert called_model.id == sample_message.id
            assert called_model.text == sample_message.text
            assert called_model.author_id == sample_message.author_id
            assert called_model.hidden == sample_message.hidden
            assert called_model.created_at == sample_message.created_at
            mock_session.commit.assert_called_once()

    async def test_should_get_by_id_found(self, repository, mock_session, sample_message):
        """Getting message by id"""
        test_model = TestMessageModel(
            id=sample_message.id,
            text=sample_message.text,
            author_id=sample_message.author_id,
            hidden=sample_message.hidden,
            created_at=sample_message.created_at
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=test_model)
        mock_session.execute.return_value = mock_result

        with patch('services.message_service.infrastructure.repositories.message_repo.MessageModel', TestMessageModel):
            # Act
            result = await repository.get_by_id(sample_message.id)

            # Assert
            mock_session.execute.assert_called_once()
            assert result is not None
            assert isinstance(result, Message)
            assert result.id == sample_message.id
            assert result.text == sample_message.text
            assert result.author_id == sample_message.author_id
            assert result.hidden == sample_message.hidden
            assert result.created_at == sample_message.created_at

    async def test_should_get_by_id_not_found(self, repository, mock_session):
        """Getting message which is not found"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute.return_value = mock_result

        with patch('services.message_service.infrastructure.repositories.message_repo.MessageModel', TestMessageModel):
            # Act
            result = await repository.get_by_id(uuid4())

            # Assert
            assert result is None

    async def test_update(self, repository, mock_session, sample_message):
        """Updating message"""
        with patch('services.message_service.infrastructure.repositories.message_repo.MessageModel', TestMessageModel):
            # Act
            await repository.update(sample_message)

            # Assert
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()


if __name__ == "__main__":
    pytest.main()
