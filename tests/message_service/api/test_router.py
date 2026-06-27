import asyncio
import unittest
from unittest.mock import Mock

from services.message_service.api.router import (
    get_publish_use_case,
    get_visibility_use_case,
    router,
)
from services.message_service.application.publish import PublishMessage
from services.message_service.application.visibility import VisibilityUseCase
from services.message_service.infrastructure.message_index import NullIndexer
from services.message_service.infrastructure.repositories.message_hash_repo import (
    MessageHashRepository,
)
from services.message_service.infrastructure.repositories.message_repo import (
    MessageRepository,
)
from services.message_service.moderation_module.pipeline import (
    HardModerationPipeline,
    SoftModerationPipeline,
)


class TestMessageRouterComposition(unittest.TestCase):
    def test_publish_factory_wires_use_case_dependencies(self):
        session = Mock()

        use_case = asyncio.run(get_publish_use_case(session))

        self.assertIsInstance(use_case, PublishMessage)
        self.assertIsInstance(use_case.repo, MessageRepository)
        self.assertIsInstance(use_case.hash_repo, MessageHashRepository)
        self.assertIsInstance(use_case.hard_pipe, HardModerationPipeline)
        self.assertIsInstance(use_case.soft_pipe, SoftModerationPipeline)
        self.assertIsInstance(use_case.indexer, NullIndexer)
        self.assertIs(use_case.repo.session, session)
        self.assertIs(use_case.hash_repo.session, session)

    def test_visibility_factory_wires_message_repository(self):
        session = Mock()

        use_case = asyncio.run(get_visibility_use_case(session))

        self.assertIsInstance(use_case, VisibilityUseCase)
        self.assertIsInstance(use_case.repo, MessageRepository)
        self.assertIs(use_case.repo.session, session)

    def test_detach_route_is_registered(self):
        detach_routes = [
            route
            for route in router.routes
            if route.path == "/messages/{message_id}/detach"
        ]

        self.assertEqual(len(detach_routes), 1)
        self.assertIn("POST", detach_routes[0].methods)


class TestNullIndexer(unittest.IsolatedAsyncioTestCase):
    async def test_index_is_noop(self):
        indexer = NullIndexer()

        result = await indexer.index(Mock(), "text")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
