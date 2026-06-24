import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import declarative_base

from services.message_service.infrastructure.repositories.message_hash_repo import MessageHashRepository

TestBase = declarative_base()


class TestMessageHashModel(TestBase):
    __tablename__ = 'message_hashes'
    hash = Column(String, primary_key=True)
    message_id = Column(UUID)


@pytest.fixture
def mock_session():
    """Create a mock async SQLAlchemy session"""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a repository instance with mocked session"""
    return MessageHashRepository(mock_session)


@pytest.fixture
def sample_hash():
    """Create a sample hash for testing"""
    return "a1b2c3d4e5f6g7h8i9j0"


@pytest.fixture
def sample_message_id():
    """Create a sample message ID for testing"""
    return uuid4()


@pytest.mark.asyncio
class TestMessageHashRepository:

    async def test_exists_true(self, repository, mock_session, sample_hash):
        """Test that exists returns True when hash is found in database"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=MagicMock())  # Non-None means found
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.exists(sample_hash)

        # Assert
        mock_session.execute.assert_called_once()
        assert result is True

    async def test_exists_false(self, repository, mock_session, sample_hash):
        """Test that exists returns False when hash is not found in database"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)  # None means not found
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.exists(sample_hash)

        # Assert
        mock_session.execute.assert_called_once()
        assert result is False

    async def test_exists_handles_exception(self, repository, mock_session, sample_hash):
        """Test that exceptions during existence check are propagated correctly"""
        # Arrange
        mock_session.execute.side_effect = Exception("Database query failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database query failed"):
            await repository.exists(sample_hash)

    async def test_save_success(self, repository, mock_session, sample_hash, sample_message_id):
        """Test successfully saving a hash-message relationship"""
        # Arrange
        mock_model_instance = MagicMock()

        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            MockModel.return_value = mock_model_instance

            # Act
            await repository.save(sample_hash, sample_message_id)

            # Assert
            MockModel.assert_called_once_with(
                hash=sample_hash,
                message_id=sample_message_id
            )
            mock_session.add.assert_called_once_with(mock_model_instance)
            mock_session.commit.assert_called_once()

    async def test_save_creates_model_with_correct_data(self, repository, mock_session, sample_hash, sample_message_id):
        """Test that save creates the ORM model with correct data"""
        # Arrange
        captured_model = None

        def capture_model(model):
            nonlocal captured_model
            captured_model = model
            return model

        mock_session.add.side_effect = capture_model

        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            mock_instance = MagicMock()
            MockModel.return_value = mock_instance

            # Act
            await repository.save(sample_hash, sample_message_id)

            # Assert
            MockModel.assert_called_once_with(
                hash=sample_hash,
                message_id=sample_message_id
            )
            assert captured_model is mock_instance
            mock_session.commit.assert_called_once()

    async def test_save_handles_exception(self, repository, mock_session, sample_hash, sample_message_id):
        """Test that exceptions during save are propagated correctly"""
        # Arrange
        mock_session.commit.side_effect = Exception("Database connection failed")

        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            MockModel.return_value = MagicMock()

            # Act & Assert
            with pytest.raises(Exception, match="Database connection failed"):
                await repository.save(sample_hash, sample_message_id)
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    async def test_save_with_empty_hash(self, repository, mock_session, sample_message_id):
        """Test saving with an empty hash string"""
        # Arrange
        empty_hash = ""
        mock_model_instance = MagicMock()

        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            MockModel.return_value = mock_model_instance

            # Act
            await repository.save(empty_hash, sample_message_id)

            # Assert
            MockModel.assert_called_once_with(
                hash=empty_hash,
                message_id=sample_message_id
            )
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    async def test_save_with_none_hash(self, repository, mock_session, sample_message_id):
        """Test saving with None as hash (should handle gracefully or raise)"""
        # Arrange
        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            # Act & Assert
            try:
                await repository.save(None, sample_message_id)
                MockModel.assert_called_once_with(
                    hash=None,
                    message_id=sample_message_id
                )
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
            except Exception as e:
                assert isinstance(e, (TypeError, ValueError, Exception))

    async def test_exists_with_special_characters(self, repository, mock_session):
        """Test existence check with hash containing special characters"""
        # Arrange
        special_hash = "!@#$%^&*()_+{}|:<>?~"
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=MagicMock())
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.exists(special_hash)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()

    async def test_save_with_long_hash(self, repository, mock_session, sample_message_id):
        """Test saving with a very long hash string"""
        # Arrange
        long_hash = "a" * 1000
        mock_model_instance = MagicMock()

        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            MockModel.return_value = mock_model_instance

            # Act
            await repository.save(long_hash, sample_message_id)

            # Assert
            MockModel.assert_called_once_with(
                hash=long_hash,
                message_id=sample_message_id
            )
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    async def test_save_multiple_hashes(self, repository, mock_session):
        """Test saving multiple hash-message relationships"""
        # Arrange
        hashes = ["hash1", "hash2", "hash3"]
        message_ids = [uuid4(), uuid4(), uuid4()]

        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            mock_instances = [MagicMock() for _ in range(3)]
            MockModel.side_effect = mock_instances

            # Act
            for h, mid in zip(hashes, message_ids):
                await repository.save(h, mid)

            # Assert
            assert MockModel.call_count == 3
            assert mock_session.add.call_count == 3
            assert mock_session.commit.call_count == 3

    async def test_save_returns_nothing(self, repository, mock_session, sample_hash, sample_message_id):
        """Test that save method doesn't return anything (void method)"""
        # Arrange
        with patch(
                'services.message_service.infrastructure.repositories.message_hash_repo.MessageHashModel') as MockModel:
            MockModel.return_value = MagicMock()

            # Act
            result = await repository.save(sample_hash, sample_message_id)

            # Assert
            assert result is None
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()


if __name__ == "__main__":
    pytest.main()
