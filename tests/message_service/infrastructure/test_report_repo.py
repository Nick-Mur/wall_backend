import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestReportRepository(unittest.TestCase):

    def setUp(self):
        self.mock_session = AsyncMock()
        self.mock_session.add = MagicMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        self.mock_session.execute = AsyncMock()

        from services.message_service.infrastructure.repositories.report_repo import ReportRepository
        self.repository = ReportRepository(self.mock_session)
        self.message_id = uuid4()
        self.report_id = uuid4()
        self.reason = "Inappropriate content"

    def test_should_save_report_successfully(self):
        """Should save a new report with pending status"""

        async def run_test():
            mock_report = MagicMock()
            mock_report.id = self.report_id
            mock_report.message_id = self.message_id
            mock_report.reason = self.reason
            mock_report.status = "pending"

            with patch('services.message_service.infrastructure.repositories.report_repo.ReportModel') as MockModel:
                MockModel.return_value = mock_report
                result = await self.repository.save(self.message_id, self.reason)

            MockModel.assert_called_once_with(
                message_id=self.message_id,
                reason=self.reason,
                status="pending"
            )
            self.mock_session.add.assert_called_once_with(mock_report)
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once_with(mock_report)
            self.assertEqual(result, mock_report)

        asyncio.run(run_test())

    def test_should_get_report_by_id(self):
        """Should find a report by its ID"""

        async def run_test():
            mock_report = MagicMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=mock_report)
            self.mock_session.execute.return_value = mock_result

            result = await self.repository.get_by_id(self.report_id)

            self.mock_session.execute.assert_called_once()
            self.assertEqual(result, mock_report)

        asyncio.run(run_test())

    def test_should_return_none_when_report_not_found(self):
        """Should return None when report does not exist"""

        async def run_test():
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=None)
            self.mock_session.execute.return_value = mock_result

            result = await self.repository.get_by_id(self.report_id)

            self.assertIsNone(result)

        asyncio.run(run_test())

    def test_should_get_reports_by_message_id(self):
        """Should get all reports for a specific message"""

        async def run_test():
            mock_reports = [MagicMock(), MagicMock(), MagicMock()]
            mock_scalars = MagicMock()
            mock_scalars.all = MagicMock(return_value=mock_reports)
            mock_result = AsyncMock()
            mock_result.scalars = MagicMock(return_value=mock_scalars)
            self.mock_session.execute.return_value = mock_result

            result = await self.repository.get_by_message_id(self.message_id)

            self.mock_session.execute.assert_called_once()
            self.assertEqual(result, mock_reports)
            self.assertEqual(len(result), 3)

        asyncio.run(run_test())

    def test_should_return_empty_list_when_no_reports(self):
        """Should return empty list when no reports exist for a message"""

        async def run_test():
            mock_scalars = MagicMock()
            mock_scalars.all = MagicMock(return_value=[])
            mock_result = AsyncMock()
            mock_result.scalars = MagicMock(return_value=mock_scalars)
            self.mock_session.execute.return_value = mock_result

            result = await self.repository.get_by_message_id(self.message_id)

            self.assertEqual(result, [])

        asyncio.run(run_test())

    def test_should_update_report_status(self):
        """Should update report status to reviewed"""

        async def run_test():
            new_status = "reviewed"

            await self.repository.update_status(self.report_id, new_status)

            self.mock_session.execute.assert_called_once()
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_update_status_to_dismissed(self):
        """Should update report status to dismissed"""

        async def run_test():
            new_status = "dismissed"

            await self.repository.update_status(self.report_id, new_status)

            self.mock_session.execute.assert_called_once()
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_raise_exception_when_save_fails(self):
        """Should raise exception when database save fails"""

        async def run_test():
            self.mock_session.commit.side_effect = Exception("Database error")

            with patch('services.message_service.infrastructure.repositories.report_repo.ReportModel') as MockModel:
                MockModel.return_value = MagicMock()

                with self.assertRaises(Exception) as context:
                    await self.repository.save(self.message_id, self.reason)

                self.assertEqual(str(context.exception), "Database error")
                self.mock_session.add.assert_called_once()
                self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_raise_exception_when_get_by_id_fails(self):
        """Should raise exception when database query fails"""

        async def run_test():
            self.mock_session.execute.side_effect = Exception("Database error")

            with self.assertRaises(Exception) as context:
                await self.repository.get_by_id(self.report_id)

            self.assertEqual(str(context.exception), "Database error")

        asyncio.run(run_test())

    def test_should_raise_exception_when_update_status_fails(self):
        """Should raise exception when status update fails"""

        async def run_test():
            self.mock_session.commit.side_effect = Exception("Database error")

            with self.assertRaises(Exception) as context:
                await self.repository.update_status(self.report_id, "reviewed")

            self.assertEqual(str(context.exception), "Database error")
            self.mock_session.execute.assert_called_once()
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_save_report_with_default_pending_status(self):
        """Should create report with pending status by default"""

        async def run_test():
            mock_report = MagicMock()

            with patch('services.message_service.infrastructure.repositories.report_repo.ReportModel') as MockModel:
                MockModel.return_value = mock_report
                await self.repository.save(self.message_id, self.reason)

            MockModel.assert_called_once_with(
                message_id=self.message_id,
                reason=self.reason,
                status="pending"
            )

        asyncio.run(run_test())

    def test_should_refresh_report_after_save(self):
        """Should refresh report after saving to get DB-generated fields"""

        async def run_test():
            mock_report = MagicMock()

            with patch('services.message_service.infrastructure.repositories.report_repo.ReportModel') as MockModel:
                MockModel.return_value = mock_report
                await self.repository.save(self.message_id, self.reason)

            self.mock_session.refresh.assert_called_once_with(mock_report)

        asyncio.run(run_test())

    def test_should_return_report_from_save(self):
        """Should return the created report from save method"""

        async def run_test():
            mock_report = MagicMock()
            mock_report.id = self.report_id

            with patch('services.message_service.infrastructure.repositories.report_repo.ReportModel') as MockModel:
                MockModel.return_value = mock_report
                result = await self.repository.save(self.message_id, self.reason)

            self.assertEqual(result.id, self.report_id)
            self.assertEqual(result, mock_report)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()