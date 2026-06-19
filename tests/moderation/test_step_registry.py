import unittest
import asyncio
from services.message_service.moderation_module.step_registry import RegistryStep
from services.message_service.moderation_module.steps.ban_words import BanWordsStep
from services.message_service.moderation_module.steps.pii import PIIStep
from services.message_service.moderation_module.steps.normalization import NormalizationStep
from services.message_service.moderation_module.step import ModerationStep


class TestRegistryStep(unittest.TestCase):
    def setUp(self):
        self.registry = RegistryStep()

    def test_should_create_ban_words_step(self):
        """Create BanWordsStep by name with required parameters"""
        # given
        step_name = "ban_words"
        forbidden_words = ["bad", "hate", "spam"]

        # when
        step = RegistryStep.create_step(step_name, forbidden_words=forbidden_words)

        # then
        self.assertIsInstance(step, BanWordsStep)
        self.assertEqual(step.forbidden_words, forbidden_words)

    def test_should_create_pii_step(self):
        """Create PIIStep by name (no parameters needed)"""
        # given
        step_name = "pii"

        # when
        step = RegistryStep.create_step(step_name)

        # then
        self.assertIsInstance(step, PIIStep)
        self.assertTrue(hasattr(step, "TEL_REG"))
        self.assertTrue(hasattr(step, "EMAIL_REG"))

    def test_should_create_normalization_step(self):
        """Create NormalizationStep by name (no parameters needed)"""
        # given
        step_name = "normalization"

        # when
        step = RegistryStep.create_step(step_name)

        # then
        self.assertIsInstance(step, NormalizationStep)
        self.assertTrue(hasattr(step, "process"))

    def test_should_create_step_with_kwargs(self):
        """Create step with additional arguments"""
        # given
        step_name = "ban_words"
        forbidden_words = ["spam", "violence", "hate"]

        # when
        step = RegistryStep.create_step(step_name, forbidden_words=forbidden_words)

        # then
        self.assertIsInstance(step, BanWordsStep)
        self.assertEqual(step.forbidden_words, forbidden_words)
        self.assertEqual(len(step.forbidden_words), 3)

    def test_should_raise_error_for_unknown_step(self):
        """Raise ValueError for unknown step name"""
        # given
        step_name = "unknown"

        # when & then
        with self.assertRaises(ValueError) as context:
            RegistryStep.create_step(step_name)

        self.assertIn("Uknown step:", str(context.exception))

    def test_should_raise_error_for_empty_step_name(self):
        """Raise ValueError for empty step name"""
        # given
        step_name = ""

        # when & then
        with self.assertRaises(ValueError) as context:
            RegistryStep.create_step(step_name)

        self.assertIn("Uknown step:", str(context.exception))

    def test_should_register_all_available_steps(self):
        """Check that all steps are registered"""
        # given
        expected_steps = ["ban_words", "pii", "normalization"]

        # when
        registered_steps = list(RegistryStep._steps.keys())

        # then
        self.assertEqual(sorted(registered_steps), sorted(expected_steps))

    def test_should_create_different_steps_with_params(self):
        """Create different types of steps with required parameters"""
        # given
        step_configs = [
            ("ban_words", {"forbidden_words": ["bad", "hate"]}),
            ("pii", {}),
            ("normalization", {})
        ]
        expected_classes = [BanWordsStep, PIIStep, NormalizationStep]

        # when & then
        for (name, params), expected_class in zip(step_configs, expected_classes):
            step = RegistryStep.create_step(name, **params)
            self.assertIsInstance(step, expected_class)

    def test_should_create_ban_words_with_custom_words(self):
        """Create BanWordsStep with custom forbidden words"""
        # given
        custom_words = ["apple", "pear", "banana"]

        # when
        step = RegistryStep.create_step("ban_words", forbidden_words=custom_words)

        # then
        self.assertIsInstance(step, BanWordsStep)
        self.assertEqual(step.forbidden_words, custom_words)

    def test_should_preserve_step_type(self):
        """Created step should preserve its type"""
        # given
        step = RegistryStep.create_step("ban_words", forbidden_words=["test"])

        # when
        is_ban_words = isinstance(step, BanWordsStep)
        is_moderation_step = isinstance(step, ModerationStep)

        # then
        self.assertTrue(is_ban_words)
        self.assertTrue(is_moderation_step)

    def test_should_create_step_without_arguments_if_possible(self):
        """Create steps that don't require arguments"""
        # given
        step_names = ["pii", "normalization"]  # Only steps without required params

        # when & then
        for name in step_names:
            step = RegistryStep.create_step(name)
            self.assertIsNotNone(step)
            self.assertIsInstance(step, ModerationStep)

    def test_should_raise_error_for_missing_required_params(self):
        """Raise TypeError when required params are missing"""
        # given
        step_name = "ban_words"

        # when & then
        with self.assertRaises(TypeError) as context:
            RegistryStep.create_step(step_name)

        self.assertIn("missing", str(context.exception).lower())

    def test_should_raise_error_with_correct_message(self):
        """Error message should contain the unknown step name"""
        # given
        step_name = "non_existent_step"

        # when & then
        with self.assertRaises(ValueError) as context:
            RegistryStep.create_step(step_name)

        self.assertIn(step_name, str(context.exception))

    def test_should_create_step_with_multiple_kwargs(self):
        """Create step with multiple keyword arguments"""
        # given
        forbidden_words = ["bad", "hate", "spam", "violence"]

        # when
        step = RegistryStep.create_step("ban_words", forbidden_words=forbidden_words)

        # then
        self.assertIsInstance(step, BanWordsStep)
        self.assertEqual(step.forbidden_words, forbidden_words)
        self.assertEqual(len(step.forbidden_words), 4)

    def test_should_be_able_to_use_step_in_pipeline(self):
        """Created step should work in pipeline"""
        # given
        from services.message_service.moderation_module.pipeline import HardModerationPipeline

        step = RegistryStep.create_step("ban_words", forbidden_words=["spam"])
        pipeline = HardModerationPipeline([step])

        # when
        result = asyncio.run(pipeline.validate("This is spam content"))

        # then
        self.assertTrue(result.is_rejected)
        self.assertEqual(result.reason.code, "BAN_WORDS")

    def test_should_return_same_type_as_direct_creation(self):
        """Registry-created step should be same as direct creation"""
        # given
        forbidden_words = ["bad", "hate"]

        # when
        registry_step = RegistryStep.create_step("ban_words", forbidden_words=forbidden_words)
        direct_step = BanWordsStep(forbidden_words)

        # then
        self.assertEqual(type(registry_step), type(direct_step))
        self.assertEqual(registry_step.forbidden_words, direct_step.forbidden_words)


if __name__ == "__main__":
    unittest.main()