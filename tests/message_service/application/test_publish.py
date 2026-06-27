import unittest
import asyncio
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
import hashlib
from uuid import UUID
from services.message_service.application.publish import PublishMessage
from services.message_service.moderation_module.step import ModerationWarning
from services.message_service.moderation_module.moderation_result import ModerationResult


class TestPublishMessage(unittest.TestCase):
    def setUp(self):
        """Create mocks before each test"""
        self.mock_message_repo = Mock()
        self.mock_hash_repo = Mock()
        self.mock_hard_pipe = Mock()
        self.mock_soft_pipe = Mock()
        self.mock_indexer = Mock()

        self.mock_hash_repo.exists = AsyncMock(return_value=False)
        self.mock_hash_repo.save = AsyncMock()
        self.mock_message_repo.save = AsyncMock()
        self.mock_message_repo.missing_ids = AsyncMock(return_value=[])
        self.mock_indexer.index = AsyncMock()

        self.service = PublishMessage(
            message_repo=self.mock_message_repo,
            hash_repo=self.mock_hash_repo,
            hard_pipe=self.mock_hard_pipe,
            soft_pipe=self.mock_soft_pipe,
            indexer=self.mock_indexer
        )

    def test_should_publish_message_successfully(self):
        """Should publish message successfully"""
        # given
        text = "My first post!!!!!"
        author_id = uuid4()
        references = [uuid4(), uuid4()]

        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        result = asyncio.run(self.service.process(text, references, author_id))

        # then
        self.assertEqual(result["status"], "published")
        self.assertEqual(result["code"], 201)
        self.assertIn("message_id", result)
        self.assertEqual(result["warnings"], [])

        self.mock_hash_repo.exists.assert_called_once()
        self.mock_hard_pipe.validate.assert_called_once_with(text)
        self.mock_soft_pipe.validate.assert_called_once_with(text)
        self.mock_message_repo.save.assert_called_once()
        self.mock_hash_repo.save.assert_called_once()
        self.mock_indexer.index.assert_called_once()

    def test_should_generate_correct_text_hash(self):
        """Should generate correct SHA256 hash for text"""
        # given
        text = "text"
        expected_hash = hashlib.sha256(text.encode()).hexdigest()

        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        self.mock_hash_repo.exists.assert_called_with(expected_hash)
        self.mock_hash_repo.save.assert_called_with(expected_hash, result["message_id"])

    def test_should_save_message_with_correct_data(self):
        """Should save message with correct data"""
        # given
        text = "Test"
        author_id = uuid4()
        references = [uuid4(), uuid4()]

        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        asyncio.run(self.service.process(text, references, author_id))

        # then
        saved_message = self.mock_message_repo.save.call_args[0][0]
        self.assertEqual(saved_message.text, text)
        self.assertEqual(saved_message.author_id, author_id)
        self.assertEqual(saved_message.references, references)
        self.assertIsInstance(saved_message.id, UUID)

    def test_should_reject_duplicate_message(self):
        """Should reject duplicate message"""
        # given
        text = "Duplicate message"
        self.mock_hash_repo.exists = AsyncMock(return_value=True)

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], 409)
        self.assertEqual(result["reason"], "Duplicate detected")

        self.mock_hard_pipe.validate.assert_not_called()
        self.mock_soft_pipe.validate.assert_not_called()
        self.mock_message_repo.save.assert_not_called()
        self.mock_hash_repo.save.assert_not_called()
        self.mock_indexer.index.assert_not_called()

    def test_should_reject_message_on_hard_moderation_fail(self):
        """Should reject message when hard moderation fails"""
        # given
        text = "Bad content"
        reason = "Contains prohibited words"

        mock_result = Mock(spec=ModerationResult)
        mock_result.is_rejected = True
        mock_result.reason = Mock()
        mock_result.reason.message = reason
        self.mock_hard_pipe.validate = AsyncMock(return_value=mock_result)

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], 422)
        self.assertEqual(result["reason"], reason)

        self.mock_soft_pipe.validate.assert_not_called()
        self.mock_message_repo.save.assert_not_called()
        self.mock_hash_repo.save.assert_not_called()
        self.mock_indexer.index.assert_not_called()

    def test_should_not_skip_hard_moderation_for_valid_message(self):
        """Should not skip hard moderation for valid message"""
        # given
        text = "Valid message"
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        asyncio.run(self.service.process(text, []))

        # then
        self.mock_hard_pipe.validate.assert_called_once_with(text)

    def test_should_collect_warnings_from_soft_moderation(self):
        """Should collect warnings from soft moderation"""
        # given
        text = "Message with warnings"
        warnings = ["Warning 1", "Warning 2", "Warning 3"]

        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))

        mock_soft_result = Mock(spec=ModerationResult)
        mock_soft_result.warnings = [
            ModerationWarning(code="W001", message=w) for w in warnings
        ]
        self.mock_soft_pipe.validate = AsyncMock(return_value=mock_soft_result)

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        self.assertEqual(result["status"], "published")
        self.assertEqual(result["warnings"], warnings)

    def test_should_reject_missing_references(self):
        text = "Message with missing reference"
        missing_reference = uuid4()

        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_message_repo.missing_ids = AsyncMock(return_value=[missing_reference])

        result = asyncio.run(self.service.process(text, [missing_reference]))

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], 400)
        self.assertIn(str(missing_reference), result["reason"])
        self.mock_soft_pipe.validate.assert_not_called()
        self.mock_message_repo.save.assert_not_called()
        self.mock_hash_repo.save.assert_not_called()
        self.mock_indexer.index.assert_not_called()

    def test_should_return_empty_warnings_list_when_no_warnings(self):
        """Should return empty warnings list when no warnings"""
        # given
        text = "Clean message"
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        self.assertEqual(result["warnings"], [])

    def test_should_continue_after_soft_moderation_warnings(self):
        """Should continue processing even with soft moderation warnings"""
        # given
        text = "Message with warnings"
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))

        mock_soft_result = Mock(spec=ModerationResult)
        mock_soft_result.warnings = [ModerationWarning(code="W001", message="Warning")]
        self.mock_soft_pipe.validate = AsyncMock(return_value=mock_soft_result)

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        self.assertEqual(result["status"], "published")
        self.mock_message_repo.save.assert_called_once()
        self.mock_indexer.index.assert_called_once()

    def test_should_index_message_after_save(self):
        """Should index message after saving"""
        # given
        text = "Message to index"
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        result = asyncio.run(self.service.process(text, []))

        # then
        message_id = result["message_id"]
        self.mock_indexer.index.assert_called_once_with(message_id, text)

    def test_should_handle_long_text(self):
        """Should handle very long text - should raise validation error"""
        # given
        text = "A" * 10000
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when / then
        import asyncio
        from services.message_service.domain.exceptions.text_validation_error import TextValidationError

        with self.assertRaises(TextValidationError) as context:
            asyncio.run(self.service.process(text, []))

        self.assertIn("Text too long", str(context.exception))
        self.mock_message_repo.save.assert_not_called()

    def test_should_handle_max_length_text(self):
        """Should handle text of maximum allowed length"""
        # given
        MAX_TEXT_LENGTH = 5000
        text = "A" * MAX_TEXT_LENGTH

        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        import asyncio
        result = asyncio.run(self.service.process(text, []))

        # then
        self.assertEqual(result["status"], "published")
        self.mock_message_repo.save.assert_called_once()

    def test_should_handle_none_author_id(self):
        """Should handle None author_id"""
        # given
        text = "Anonymous message"
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        import asyncio
        asyncio.run(self.service.process(text, [], author_id=None))

        # then
        saved_message = self.mock_message_repo.save.call_args[0][0]
        self.assertIsNone(saved_message.author_id)

    def test_should_handle_empty_references(self):
        """Should handle empty references list"""
        # given
        text = "Message without references"
        self.mock_hard_pipe.validate = AsyncMock(return_value=Mock(is_rejected=False))
        self.mock_soft_pipe.validate = AsyncMock(return_value=Mock(warnings=[]))

        # when
        import asyncio
        asyncio.run(self.service.process(text, []))

        # then
        saved_message = self.mock_message_repo.save.call_args[0][0]
        self.assertEqual(saved_message.references, [])


if __name__ == "__main__":
    unittest.main()
