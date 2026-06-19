import unittest
import asyncio
from services.message_service.moderation_module.steps.ban_words import BanWordsStep
from services.message_service.domain.moderation import ModerationReason


class TestBanWordsStep(unittest.TestCase):
    def setUp(self):
        self.forbidden_words = ["hate", "spam", "violence"]
        self.ban_step = BanWordsStep(self.forbidden_words)

    def test_should_initialize_with_forbidden_words(self):
        """Test initialization with forbidden words"""
        # given
        words = ["hate", "Lorem Ipsum"]

        # when
        step = BanWordsStep(words)

        # then
        self.assertEqual(step.forbidden_words, words)
        self.assertEqual(len(step.forbidden_words), 2)

    def test_should_return_none_for_clean_text(self):
        """Clean text should pass moderation"""
        # given
        text = "London bridge is falling down"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_detect_banned_word_in_lowercase(self):
        """Detect banned word in lowercase"""
        # given
        text = "I hate u"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsInstance(result, ModerationReason)
        self.assertEqual(result.code, "BAN_WORDS")
        self.assertEqual(result.message, "Banned word detected: hate")
        self.assertEqual(result.to_message(), "Banned word detected: hate")

    def test_should_detect_banned_word_in_uppercase(self):
        """Detect banned word in uppercase"""
        # given
        text = "I HATE u"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsInstance(result, ModerationReason)
        self.assertEqual(result.code, "BAN_WORDS")
        self.assertEqual(result.message, "Banned word detected: hate")

    def test_should_detect_banned_word_in_mixed_case(self):
        """Detect banned word in mixed case"""
        # given
        text = "This is sPaM"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsInstance(result, ModerationReason)
        self.assertEqual(result.code, "BAN_WORDS")
        self.assertEqual(result.message, "Banned word detected: spam")

    def test_should_return_none_for_empty_text(self):
        """Empty text should pass moderation"""
        # given
        text = ""

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_detect_partial_match_with_numbers(self):
        """Detect banned word with numbers"""
        # given
        text = "spam12345"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsInstance(result, ModerationReason)
        self.assertEqual(result.code, "BAN_WORDS")
        self.assertEqual(result.message, "Banned word detected: spam")

    def test_should_be_async(self):
        """Process method should be async"""
        # given
        import inspect

        # when
        is_async = inspect.iscoroutinefunction(self.ban_step.process)

        # then
        self.assertTrue(is_async)

    def test_should_return_moderation_reason_with_correct_code(self):
        """Return ModerationReason with correct code"""
        # given
        text = "This is spam content"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsInstance(result, ModerationReason)
        self.assertEqual(result.code, "BAN_WORDS")
        self.assertTrue(result.message.startswith("Banned word detected:"))

    def test_should_detect_multiple_banned_words_in_text(self):
        """Detect multiple banned words in text"""
        # given
        text = "I hate spam and violence"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertEqual(result.message, "Banned word detected: hate")


if __name__ == "__main__":
    unittest.main()
