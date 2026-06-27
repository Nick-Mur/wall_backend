import unittest

from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.dialects import postgresql

from services.message_service.infrastructure.db_models.message import MessageModel


class TestMessageModelFts(unittest.TestCase):
    def test_messages_table_has_generated_tsv_column(self):
        table_sql = str(
            CreateTable(MessageModel.__table__).compile(dialect=postgresql.dialect())
        )

        self.assertIn("tsv TSVECTOR", table_sql)
        self.assertIn("GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED", table_sql)

    def test_messages_table_has_gin_tsv_index(self):
        index = next(
            idx for idx in MessageModel.__table__.indexes if idx.name == "ix_messages_tsv"
        )
        index_sql = str(CreateIndex(index).compile(dialect=postgresql.dialect()))

        self.assertIn("CREATE INDEX ix_messages_tsv ON messages USING gin (tsv)", index_sql)


if __name__ == "__main__":
    unittest.main()
