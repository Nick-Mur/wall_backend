import unittest
import asyncio
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime

from services.message_service.application.visibility import VisibilityUseCase, VisibilityError


class TestVisibilityUseCase(unittest.TestCase):

    def setUp(self):
        self.mock_message_repo = Mock()
        self.mock_message = Mock()
        self.mock_message.id = uuid4()
        self.mock_message.text = "Test message"
        self.mock_message.author_id = uuid4()
        self.mock_message.created_at = datetime.utcnow()

        # Настраиваем репозиторий
        self.mock_message_repo.get_by_id = AsyncMock(return_value=self.mock_message)
        self.mock_message_repo.update = AsyncMock()

        self.use_case = VisibilityUseCase(
            message_repo=self.mock_message_repo
        )

    def test_should_hide_message_successfully(self):
        """Should hide message successfully"""
        # given
        message_id = uuid4()

        # when
        import asyncio
        asyncio.run(self.use_case.hide(message_id))

        # then
        self.mock_message_repo.get_by_id.assert_called_once_with(message_id)
        self.mock_message.hide.assert_called_once()
        self.mock_message_repo.update.assert_called_once_with(self.mock_message)

    def test_should_raise_error_when_hiding_nonexistent_message(self):
        """Should raise VisibilityError when hiding non-existent message"""
        # given
        message_id = uuid4()
        self.mock_message_repo.get_by_id = AsyncMock(return_value=None)

        # when / then
        import asyncio
        with self.assertRaises(VisibilityError) as context:
            asyncio.run(self.use_case.hide(message_id))

        self.assertEqual(str(context.exception), "Message not found")
        self.mock_message.hide.assert_not_called()
        self.mock_message_repo.update.assert_not_called()

    def test_should_hide_already_hidden_message(self):
        """Should hide already hidden message"""
        # given
        message_id = uuid4()
        self.mock_message.hide = Mock()

        # when
        asyncio.run(self.use_case.hide(message_id))
        asyncio.run(self.use_case.hide(message_id))

        # then
        self.assertEqual(self.mock_message.hide.call_count, 2)
        self.assertEqual(self.mock_message_repo.update.call_count, 2)

    def test_should_detach_message_successfully(self):
        """Should detach message successfully"""
        # given
        message_id = uuid4()

        # when
        import asyncio
        asyncio.run(self.use_case.detach(message_id))

        # then
        self.mock_message_repo.get_by_id.assert_called_once_with(message_id)
        self.mock_message.detach.assert_called_once()
        self.mock_message_repo.update.assert_called_once_with(self.mock_message)

    def test_should_detach_already_detached_message(self):
        """Should detach already detached message"""
        # given
        message_id = uuid4()
        self.mock_message.detach = Mock()

        # when
        asyncio.run(self.use_case.detach(message_id))
        asyncio.run(self.use_case.detach(message_id))

        # then
        self.assertEqual(self.mock_message.detach.call_count, 2)
        self.assertEqual(self.mock_message_repo.update.call_count, 2)

    def test_should_erase_message_successfully(self):
        """Should erase message successfully"""
        # given
        message_id = uuid4()

        # when
        asyncio.run(self.use_case.erase(message_id))

        # then
        self.mock_message_repo.get_by_id.assert_called_once_with(message_id)
        self.mock_message.erase.assert_called_once()
        self.mock_message_repo.update.assert_called_once_with(self.mock_message)

    def test_should_erase_already_erased_message(self):
        """Should erase already erased message"""
        # given
        message_id = uuid4()
        self.mock_message.erase = Mock()

        # when
        asyncio.run(self.use_case.erase(message_id))
        asyncio.run(self.use_case.erase(message_id))

        # then
        self.assertEqual(self.mock_message.erase.call_count, 2)
        self.assertEqual(self.mock_message_repo.update.call_count, 2)

    def test_should_perform_multiple_operations_on_same_message(self):
        """Should perform multiple visibility operations on same message"""
        # given
        message_id = uuid4()

        # when
        import asyncio
        asyncio.run(self.use_case.hide(message_id))
        asyncio.run(self.use_case.detach(message_id))
        asyncio.run(self.use_case.erase(message_id))

        # then
        self.assertEqual(self.mock_message_repo.get_by_id.call_count, 3)
        self.mock_message.hide.assert_called_once()
        self.mock_message.detach.assert_called_once()
        self.mock_message.erase.assert_called_once()
        self.assertEqual(self.mock_message_repo.update.call_count, 3)


if __name__ == "__main__":
    unittest.main()
