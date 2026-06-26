import unittest

import pytest

# Qdrant is a stub for now.
# Skip this module.
pytest.importorskip("qdrant_client")

from libs.qdrant.client import AsyncQdrantClient, QdrantClientFactory


class TestQdrantClient(unittest.TestCase):
    def setUp(self):
        self.default = {
            "qdrant": {
                "host": "localhost",
                "port": 6334,
                "api_key": "apiiii_keyyy",
                "timeot": 10
            }
        }

    def test_should_initialize_with_default(self):
        """Initializing with empty config"""
        # given
        config = {}

        # when
        client = QdrantClientFactory(config)

        # then
        self.assertEqual(client._host, "localhost")
        self.assertIsNone(client._port)
        self.assertIsNone(client._api_key)
        self.assertEqual(client._timeout, 10)

    def test_should_initialize_with_custom(self):
        """Initializing with custom values"""
        # given
        config = {"qdrant": {
            "host": "localhost",
            "port": 6334,
            "api_key": "iamkey",
            "timeout": 400}
        }

        # when
        client = QdrantClientFactory(config)

        # then
        self.assertEqual(client._host, "localhost")
        self.assertEqual(client._port, 6334)
        self.assertEqual(client._api_key, "iamkey")
        self.assertEqual(client._timeout, 400)

    def test_should_use_default(self):
        """Using default values"""
        # given
        config = {"qdrant": {
            "port": 6334
        }
        }

        # when
        client = QdrantClientFactory(config)

        # then
        self.assertEqual(client._timeout, 10)
        self.assertEqual(client._host, "localhost")

    def test_should_create_async_client(self):
        """Returning correct type"""
        # give
        config = self.default
        factory = QdrantClientFactory(config)

        # when
        client = factory.create_async_client()

        # then
        self.assertIsInstance(client, AsyncQdrantClient)


if __name__ == "__main__":
    unittest.main()
