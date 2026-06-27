import unittest

from pydantic import ValidationError

from services.message_service.api.schemas import SubmitRequest


class TestSubmitRequest(unittest.TestCase):
    def test_should_reject_empty_text(self):
        with self.assertRaises(ValidationError):
            SubmitRequest(text="", references=[])

    def test_should_reject_whitespace_text(self):
        with self.assertRaises(ValidationError):
            SubmitRequest(text="   ", references=[])

    def test_should_strip_text(self):
        request = SubmitRequest(text="  searchable message  ", references=[])

        self.assertEqual(request.text, "searchable message")


if __name__ == "__main__":
    unittest.main()
