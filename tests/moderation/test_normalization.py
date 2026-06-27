import unittest
from services.message_service.moderation_module.steps.normalization import NormalizationStep
from services.message_service.domain.moderation import ModerationWarning


class TestNormalizationStep(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.norm_step = NormalizationStep()

    async def test_should_return_warning_for_too_many_spaces(self):
        """Return warning when text has 4 or more spaces in a row"""
        # given
        text = "Hello    world"  # 4

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")
        self.assertEqual(result.message, "Text has a lot of spaces")

    async def test_should_return_warning_for_too_many_tabs(self):
        """Return warning when text has 4 or more tabs in a row"""
        # given
        text = "Hello\t\t\t\tworld"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")

    async def test_should_return_warning_for_mixed_spaces_and_tabs(self):
        """Return warning when text has too many spaces and tabs mixed"""
        # given
        text = "Hello   \t  \t world"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")

    async def test_should_accept_exactly_3_spaces(self):
        """Accept text with exactly 3 spaces (MAX_SPACES_SEQUENCE = 3)"""
        # given
        text = "Hello   world"  # 3

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_accept_less_than_3_spaces(self):
        """Accept text with less than 3 spaces"""
        # given
        text = "Hello world"  # 1

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_warning_for_leading_spaces(self):
        """Return warning when text starts with space"""
        # given
        text = " Hello world"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")
        self.assertEqual(result.message, "There are leading or trailing whitespaces")

    async def test_should_return_warning_for_trailing_spaces(self):
        """Return warning when text ends with space"""
        # given
        text = "Hello world "

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")
        self.assertEqual(result.message, "There are leading or trailing whitespaces")

    async def test_should_return_warning_for_leading_and_trailing_spaces(self):
        """Return warning when text has both leading and trailing spaces"""
        # given
        text = " Hello world "

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")

    async def test_should_return_warning_for_too_many_newlines(self):
        """Return warning when text has 4 or more newlines in a row"""
        # given
        text = "Hello\n\n\n\nworld"  # 4

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "NEWLINES")
        self.assertEqual(result.message, "Text has a lot of newlines")

    async def test_should_accept_exactly_3_newlines(self):
        """Accept text with exactly 3 newlines (MAX_NEWLINES_SEQUENCE = 3)"""
        # given
        text = "Hello\n\n\nworld"  # 3

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_accept_less_than_3_newlines(self):
        """Accept text with less than 3 newlines"""
        # given
        text = "Hello\nworld"  # 1

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_warning_for_mixed_newlines_and_spaces(self):
        """Return warning when text has too many newlines and spaces mixed"""
        # given
        text = "Hello\n\n\n\n   world"  # 4

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "NEWLINES")

    async def test_should_return_none_for_clean_text(self):
        """Return None for clean text without issues"""
        # given
        text = "Hello world! This is a clean text"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_none_for_empty_text(self):
        """Return None for empty text"""
        # given
        text = ""

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_none_for_text_with_single_space(self):
        """Return None for text with single space between words"""
        # given
        text = "Hello world"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_none_for_text_with_single_newline(self):
        """Return None for text with single newline"""
        # given
        text = "Hello\nworld"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_none_for_text_with_2_spaces(self):
        """Return None for text with 2 spaces (less than MAX)"""
        # given
        text = "Hello  world"  # 2

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_return_none_for_text_with_2_newlines(self):
        """Return None for text with 2 newlines (less than MAX)"""
        # given
        text = "Hello\n\nworld"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsNone(result)

    async def test_should_detect_spaces_before_newlines(self):
        """Detect spaces issue first, then newlines"""
        # given
        text = "Hello    world\n\n\n\n"  # 4 spaces and 4 newlines

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")

    async def test_should_handle_text_with_only_spaces(self):
        """Handle text with only spaces"""
        # given
        text = "     "  # 5

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")

    async def test_should_handle_text_with_only_newlines(self):
        """Handle text with only newlines"""
        # given
        text = "\n\n\n\n\n"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "NEWLINES")

    async def test_should_handle_very_long_text(self):
        """Handle very long text with many spaces"""
        # given
        text = "Hello" + " " * 10 + "world"

        # when
        result = await self.norm_step.process(text)

        # then
        self.assertIsInstance(result, ModerationWarning)
        self.assertEqual(result.code, "SPACES")


if __name__ == "__main__":
    unittest.main(verbosity=2)
