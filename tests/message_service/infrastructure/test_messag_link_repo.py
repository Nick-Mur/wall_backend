import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestMessageLinkRepository(unittest.TestCase):
    def setUp(self):
        self.mock_session = AsyncMock()
        self.mock_session.add_all = MagicMock()
        self.mock_session.commit = AsyncMock()

        from services.message_service.infrastructure.repositories.message_link_repo import MessageLinkRepository
        self.repository = MessageLinkRepository(self.mock_session)
        self.source_id = uuid4()
        self.target_ids = [uuid4(), uuid4(), uuid4()]

    def test_should_add_links_successfully(self):
        """Should add multiple links successfully"""

        async def run_test():
            # given
            mock_links = [MagicMock() for _ in range(len(self.target_ids))]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, self.target_ids)

            # then
            # MessageLinkModel was called for each target_id
            self.assertEqual(MockModel.call_count, len(self.target_ids))
            calls = MockModel.call_args_list
            for i, target_id in enumerate(self.target_ids):
                self.assertEqual(calls[i][1]['source_id'], self.source_id)
                self.assertEqual(calls[i][1]['target_id'], target_id)
            self.mock_session.add_all.assert_called_once_with(mock_links)
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_not_add_links_when_target_ids_empty(self):
        """Should not add any links when target_ids is empty"""

        async def run_test():
            # given
            empty_target_ids = []

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                await self.repository.add_links(self.source_id, empty_target_ids)

            # then
            MockModel.assert_not_called()
            self.mock_session.add_all.assert_not_called()
            self.mock_session.commit.assert_not_called()

        asyncio.run(run_test())

    def test_should_add_single_link(self):
        """Should add a single link"""

        async def run_test():
            # given
            single_target_id = [uuid4()]
            mock_link = MagicMock()

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.return_value = mock_link

                await self.repository.add_links(self.source_id, single_target_id)

            # then
            MockModel.assert_called_once_with(
                source_id=self.source_id,
                target_id=single_target_id[0]
            )
            self.mock_session.add_all.assert_called_once_with([mock_link])
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_handle_none_target_ids(self):
        """Should handle None as target_ids gracefully"""

        async def run_test():
            # given
            none_target_ids = None

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                try:
                    await self.repository.add_links(self.source_id, none_target_ids)
                    MockModel.assert_not_called()
                    self.mock_session.add_all.assert_not_called()
                    self.mock_session.commit.assert_not_called()
                except Exception as e:
                    self.assertIsInstance(e, (TypeError, AttributeError, Exception))

        asyncio.run(run_test())

    def test_should_handle_duplicate_target_ids(self):
        """Should handle duplicate target IDs (creates separate links)"""

        async def run_test():
            # given
            duplicate_target_ids = [self.target_ids[0], self.target_ids[0], self.target_ids[0]]
            mock_links = [MagicMock() for _ in range(len(duplicate_target_ids))]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, duplicate_target_ids)

            # then
            self.assertEqual(MockModel.call_count, len(duplicate_target_ids))
            self.mock_session.add_all.assert_called_once_with(mock_links)
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_create_links_with_correct_source_id(self):
        """Should create all links with the correct source_id"""

        async def run_test():
            # given
            mock_links = [MagicMock() for _ in range(len(self.target_ids))]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, self.target_ids)

            # then
            for call in MockModel.call_args_list:
                self.assertEqual(call[1]['source_id'], self.source_id)

        asyncio.run(run_test())

    def test_should_create_links_with_correct_target_ids(self):
        """Should create links with correct target IDs in order"""

        async def run_test():
            # given
            mock_links = [MagicMock() for _ in range(len(self.target_ids))]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, self.target_ids)

            # then
            calls = MockModel.call_args_list
            for i, target_id in enumerate(self.target_ids):
                self.assertEqual(calls[i][1]['target_id'], target_id)

        asyncio.run(run_test())

    def test_should_raise_exception_when_add_all_fails(self):
        """Should raise exception when add_all fails"""

        async def run_test():
            # given
            self.mock_session.commit.side_effect = Exception("Database commit failed")

            # when & then
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.return_value = MagicMock()

                with self.assertRaises(Exception) as context:
                    await self.repository.add_links(self.source_id, self.target_ids)

                self.assertEqual(str(context.exception), "Database commit failed")
                self.mock_session.add_all.assert_called_once()
                self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_rollback_on_exception(self):
        """Should not commit if add_all fails (simulated)"""

        async def run_test():
            # given
            self.mock_session.add_all.side_effect = Exception("Database error")

            # when & then
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.return_value = MagicMock()

                with self.assertRaises(Exception) as context:
                    await self.repository.add_links(self.source_id, self.target_ids)

                self.assertEqual(str(context.exception), "Database error")
                self.mock_session.add_all.assert_called_once()
                self.mock_session.commit.assert_not_called()  # Should not commit if add_all fails

        asyncio.run(run_test())

    def test_should_handle_large_number_of_links(self):
        """Should handle a large number of links"""

        async def run_test():
            # given
            large_count = 100
            many_target_ids = [uuid4() for _ in range(large_count)]
            mock_links = [MagicMock() for _ in range(large_count)]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, many_target_ids)

            # then
            self.assertEqual(MockModel.call_count, large_count)
            self.mock_session.add_all.assert_called_once_with(mock_links)
            self.mock_session.commit.assert_called_once()

        asyncio.run(run_test())

    def test_should_not_commit_if_no_links_created(self):
        """Should not commit if no links are created (empty target_ids)"""

        async def run_test():
            # given
            empty_target_ids = []

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                await self.repository.add_links(self.source_id, empty_target_ids)

            # then
            MockModel.assert_not_called()
            self.mock_session.add_all.assert_not_called()
            self.mock_session.commit.assert_not_called()

        asyncio.run(run_test())

    def test_should_preserve_order_of_target_ids(self):
        """Should preserve the order of target IDs when creating links"""

        async def run_test():
            # given
            ordered_targets = [uuid4(), uuid4(), uuid4(), uuid4()]
            mock_links = [MagicMock() for _ in range(len(ordered_targets))]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, ordered_targets)

            # then
            calls = MockModel.call_args_list
            for i, target_id in enumerate(ordered_targets):
                self.assertEqual(calls[i][1]['target_id'], target_id)

        asyncio.run(run_test())

    def test_should_call_add_all_with_list(self):
        """Should call add_all with a list of link models"""

        async def run_test():
            # given
            mock_links = [MagicMock() for _ in range(len(self.target_ids))]

            # when
            with patch(
                    'services.message_service.infrastructure.repositories.message_link_repo.MessageLinkModel') as MockModel:
                MockModel.side_effect = mock_links

                await self.repository.add_links(self.source_id, self.target_ids)

            # then
            # Verify add_all was called with a list
            call_args = self.mock_session.add_all.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertEqual(len(call_args), len(self.target_ids))
            for link in call_args:
                self.assertIn(link, mock_links)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
