import unittest
import asyncio
from services.message_service.infrastructure.repositories.moderation_log_repo import ModerationLogRepository
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestModerationLogRepository(unittest.TestCase):
    def setUp(self):
        self.mock_session = AsyncMock()
        self.mock_session.add = MagicMock()
        self.mock_session.commit = AsyncMock()

        # Import here to avoid circular imports
        self.repository = ModerationLogRepository(self.mock_session)
        self.message_id = uuid4()

    def test_should_save_moderation_log_with_warnings_and_reason(self):
        """Should save moderation log with warnings and reason"""
        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "REJECTED"
            result.warnings = [
                MagicMock(message="Contains profanity"),
                MagicMock(message="Looks like spam")
            ]
            result.reason = MagicMock(message="Content violates community guidelines")

            mock_log_entry = MagicMock()

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                with patch(
                        'services.message_service.infrastructure.repositories.moderation_log_repo.uuid4') as mock_uuid:
                    mock_uuid.return_value = uuid4()
                    MockModel.return_value = mock_log_entry

                    await self.repository.save(self.message_id, result)

            # then
            MockModel.assert_called_once()
            call_args = MockModel.call_args[1]  # kwargs
            self.assertEqual(call_args['message_id'], self.message_id)
            self.assertEqual(call_args['verdict'], "REJECTED")

            # Check details
            details = call_args['details']
            self.assertEqual(details['warnings'], [
                "Contains profanity",
                "Looks like spam"
            ])
            self.assertEqual(details['reason'], "Content violates community guidelines")

            self.mock_session.add.assert_called_once_with(mock_log_entry)
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_moderation_log_without_warnings(self):
        """Should save moderation log without warnings when empty list provided"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "APPROVED"
            result.warnings = []
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            MockModel.assert_called_once()
            details = MockModel.call_args[1]['details']
            self.assertEqual(details['warnings'], [])
            self.assertIsNone(details['reason'])
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_moderation_log_without_reason(self):
        """Should save moderation log without reason when None provided"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "FLAGGED"
            result.warnings = [MagicMock(message="Suspicious content")]
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            MockModel.assert_called_once()
            details = MockModel.call_args[1]['details']
            self.assertEqual(details['warnings'], ["Suspicious content"])
            self.assertIsNone(details['reason'])
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_moderation_log_for_approved_message(self):
        """Should save moderation log for approved message"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "APPROVED"
            result.warnings = []
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            MockModel.assert_called_once_with(
                id=MockModel.call_args[1]['id'],
                message_id=self.message_id,
                verdict="APPROVED",
                details={
                    'warnings': [],
                    'reason': None
                }
            )
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_moderation_log_for_rejected_message(self):
        """Should save moderation log for rejected message with all details"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "REJECTED"
            result.warnings = [
                MagicMock(message="Contains profanity"),
                MagicMock(message="Looks like spam")
            ]
            result.reason = MagicMock(message="Content violates community guidelines")

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            MockModel.assert_called_once()
            call_args = MockModel.call_args[1]
            self.assertEqual(call_args['verdict'], "REJECTED")
            self.assertEqual(len(call_args['details']['warnings']), 2)
            self.assertEqual(call_args['details']['reason'], "Content violates community guidelines")
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_moderation_log_for_flagged_message(self):
        """Should save moderation log for flagged message"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "FLAGGED"
            result.warnings = [MagicMock(message="Suspicious content")]
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            MockModel.assert_called_once()
            call_args = MockModel.call_args[1]
            self.assertEqual(call_args['verdict'], "FLAGGED")
            self.assertEqual(len(call_args['details']['warnings']), 1)
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_generate_unique_id_for_each_log(self):
        """Should generate unique ID for each moderation log entry"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "APPROVED"
            result.warnings = []
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                with patch(
                        'services.message_service.infrastructure.repositories.moderation_log_repo.uuid4') as mock_uuid:
                    mock_uuid.side_effect = [uuid4(), uuid4()]
                    MockModel.return_value = MagicMock()

                    await self.repository.save(self.message_id, result)
                    await self.repository.save(self.message_id, result)

            # then
            self.assertEqual(MockModel.call_count, 2)
            id1 = MockModel.call_args_list[0][1]['id']
            id2 = MockModel.call_args_list[1][1]['id']
            self.assertNotEqual(id1, id2)

        asyncio.run(run_test())

    def test_should_convert_warnings_to_messages_correctly(self):
        """Should convert warning objects to messages correctly"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "FLAGGED"
            result.warnings = [MagicMock(message="Custom warning message")]
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            details = MockModel.call_args[1]['details']
            self.assertEqual(details['warnings'], ["Custom warning message"])
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_handle_multiple_warnings(self):
        """Should handle multiple warnings in a single log entry"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "REJECTED"
            result.warnings = [
                MagicMock(message="Warning 1"),
                MagicMock(message="Warning 2"),
                MagicMock(message="Warning 3")
            ]
            result.reason = MagicMock(message="Multiple violations")

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            details = MockModel.call_args[1]['details']
            self.assertEqual(len(details['warnings']), 3)
            self.assertEqual(details['warnings'], ["Warning 1", "Warning 2", "Warning 3"])
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_raise_exception_when_save_fails(self):
        """Should raise exception when database save fails"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "APPROVED"
            result.warnings = []
            result.reason = None
            self.mock_session.commit.side_effect = Exception("Database connection failed")

            # when & then
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                with self.assertRaises(Exception) as context:
                    await self.repository.save(self.message_id, result)

                self.assertEqual(str(context.exception), "Database connection failed")
                self.mock_session.add.assert_called_once()
                self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_log_with_reason_that_has_no_message(self):
        """Should handle reason with None message"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "REJECTED"
            result.warnings = [MagicMock(message="Warning")]
            result.reason = MagicMock(message=None)

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            details = MockModel.call_args[1]['details']
            self.assertIsNone(details['reason'])
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_preserve_message_id_in_log(self):
        """Should preserve message ID in the log entry"""

        async def run_test():
            # given
            message_id = uuid4()
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "APPROVED"
            result.warnings = []
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(message_id, result)

            # then
            self.assertEqual(MockModel.call_args[1]['message_id'], message_id)
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_log_with_single_warning(self):
        """Should save log with single warning"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "FLAGGED"
            result.warnings = [MagicMock(message="Single warning")]
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            details = MockModel.call_args[1]['details']
            self.assertEqual(len(details['warnings']), 1)
            self.assertEqual(details['warnings'][0], "Single warning")
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_log_with_verdict_as_string(self):
        """Should save verdict as string value"""

        async def run_test():
            # given
            result = MagicMock()
            result.verdict = MagicMock()
            result.verdict.value = "PENDING"
            result.warnings = []
            result.reason = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.moderation_log_repo.ModerationLogModel') as MockModel:
                MockModel.return_value = MagicMock()

                await self.repository.save(self.message_id, result)

            # then
            self.assertEqual(MockModel.call_args[1]['verdict'], "PENDING")
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
