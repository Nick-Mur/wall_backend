import unittest
import asyncio
import re
from services.message_service.moderation_module.steps.pii import PIIStep
from services.message_service.domain.moderation import ModerationWarning


class TestPIIStep(unittest.TestCase):
    def setUp(self):
        self.pii_step = PIIStep()

    def test_should_detect_phone_with_plus7_and_spaces(self):
        """Detect phone with +7 and spaces"""
        # given
        text = "Bla bla bla +7 999 123 45 66"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")
        self.assertEqual(result.message, "Phone number is detected")

    def test_should_detect_phone_with_plus7_and_dashes(self):
        """Detect phone with +7 and dashes"""
        # given
        text = "Bla bla bla +7-999-123-45-67 Bla bla bla"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")

    def test_should_detect_phone_with_8_and_parentheses(self):
        """Detect phone with 8 and parentheses"""
        # given
        text = "Bla bla bla 8 (999) 123-45-66"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")

    def test_should_detect_phone_with_7_and_parentheses(self):
        """Detect phone with 7 and parentheses"""
        # given
        text = "Bla bla bla 7(999)1234566"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")

    def test_should_detect_phone_without_separators(self):
        """Detect phone without separators"""
        # given
        text = "My number is 89991234567"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")

    def test_should_detect_phone_with_mixed_format(self):
        """Detect phone with mixed format"""
        # given
        text = "8(999)123-45-67 Bla bla bla"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")

    def test_should_detect_simple_email(self):
        """Detect simple email"""
        # given
        text = "Contact me at test@gmail.com"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_EMAIL")
        self.assertEqual(result.message, "Email is detected")

    def test_should_detect_email_with_dots(self):
        """Detect email with dots"""
        # given
        text = "My email is familiya.imya@mail.dot.ru"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_EMAIL")

    def test_should_detect_email_with_underscore(self):
        """Detect email with underscore"""
        # given
        text = "user_name@gmail.com"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_EMAIL")

    def test_should_detect_email_with_hyphen(self):
        """Detect email with hyphen"""
        # given
        text = "user-name@domain-site.com"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_EMAIL")

    def test_should_detect_email_with_numbers(self):
        """Detect email with numbers"""
        # given
        text = "user123@domain123.com"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_EMAIL")

    def test_should_return_none_for_text_without_pii(self):
        """Return None for text without any PII"""
        # given
        text = "Hello, this is a completely clean message!"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_return_none_for_empty_text(self):
        """Return None for empty text"""
        # given
        text = ""

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_return_none_for_text_with_only_numbers(self):
        """Return None for text with only numbers (not phone)"""
        # given
        text = "1234567890"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_return_none_for_text_with_only_symbols(self):
        """Return None for text with only symbols"""
        # given
        text = "!@#$%^&*()"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_return_none_for_local_part_without_at(self):
        """Return None for text that looks like email but without @"""
        # given
        text = "username.example.com"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_return_none_for_incomplete_phone(self):
        """Return None for incomplete phone number"""
        # given
        text = "+7 999 123"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_handle_text_with_newlines(self):
        """Handle text with newlines"""
        # given
        text = "My phone is\n+7 999 123 45 67\n at 7 am"

        # when
        result = asyncio.run(self.pii_step.process(text))

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "PII_PHONE")


if __name__ == "__main__":
    unittest.main()
