import unittest
import asyncio
from services.message_service.moderation_module.steps.ban_words import BanWordsStep


class TestBanWordsStep(unittest.TestCase):
    def setUp(self):
        self.forbidden_words = ["hate", "spam", "violence"]
        self.ban_step = BanWordsStep(self.forbidden_words)

    def test_should_initialize_with_forbidden_words(self):
        """Initializing with forbidden words"""
        # given
        words = ["hate", "Lorem Ipsum"]

        # when
        step = BanWordsStep(words)

        # then
        self.assertEqual(step.forbidden_words, words)
        self.assertEqual(len(step.forbidden_words), 2)

    def test_should_return_none_for_clean_text(self):
        """Non forbidden text pass moderation"""
        # given
        text = "London bridge is falling down"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_detect_banned_word_in_lowercase(self):
        """Finding a bad word in low register"""
        # given
        text = "I hate u"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertEqual(result, "Banned word detected: hate")

    def test_should_detect_banned_word_in_uppercase(self):
        """Finding a bad word in high register"""
        # given
        text = "I HATE u"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertEqual(result, "Banned word detected: hate")

    def test_should_detect_banned_word_in_mixed_case(self):
        """Finding a bad word in puzzled register"""
        # given
        text = "This is sPaM"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertEqual(result, "Banned word detected: spam")

    def test_should_return_none_for_empty_text(self):
        """The empty text passing moderation"""
        # given
        text = ""

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertIsNone(result)

    def test_should_not_detect_partial_match(self):
        """Finding a bad word in a part of text"""
        # given
        text = "spambot"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertEqual(result, "Banned word detected: spam")

    def test_should_detect_partial_match_with_numbers(self):
        """Finding a bad word in a part of text"""
        # given
        text = "spam12345"

        # when
        result = asyncio.run(self.ban_step.process(text))

        # then
        self.assertEqual(result, "Banned word detected: spam")


    def test_should_be_async(self):
        """Moderation is async"""
        # given
        import inspect

        # when
        is_async = inspect.iscoroutinefunction(self.ban_step.process)

        # then
        self.assertTrue(is_async)


if __name__ == "__main__":
    unittest.main()
