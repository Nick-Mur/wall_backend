import unittest
import asyncio
from services.message_service.moderation_module.pipeline import SoftModerationPipeline, HardModerationPipeline
from services.message_service.moderation_module.step import ModerationStep
from services.message_service.domain.moderation import ModerationVerdict, ModerationWarning, ModerationReason


# ============= MOCK STEPS =============

class PassStep(ModerationStep):
    async def process(self, text: str):
        return None


class WarningStep(ModerationStep):
    def __init__(self, code="SPAM", message="Potential spam detected"):
        self.code = code
        self.message = message

    async def process(self, text: str):
        return ModerationWarning(code=self.code, message=self.message)


class RejectStep(ModerationStep):
    def __init__(self, code="BAN_WORDS", message="Banned word detected"):
        self.code = code
        self.message = message

    async def process(self, text: str):
        return ModerationReason(code=self.code, message=self.message)


# ============= TESTS FOR HARD MODERATION PIPELINE =============

class TestHardModerationPipeline(unittest.TestCase):
    def setUp(self):
        self.text = "Test message"

    def test_should_return_approved_when_no_issues(self):
        """Return APPROVED when all steps pass"""
        # given
        steps = [PassStep(), PassStep()]
        pipeline = HardModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(result.is_rejected)
        self.assertEqual(len(result.warnings), 0)

    def test_should_ignore_warnings(self):
        """Ignore warnings and return APPROVED"""
        # given
        steps = [WarningStep()]
        pipeline = HardModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(result.is_rejected)
        self.assertEqual(len(result.warnings), 0)

    def test_should_reject_on_first_reason(self):
        """Reject immediately on ModerationReason"""
        # given
        steps = [
            WarningStep(),
            RejectStep(code="HATE_SPEECH", message="Hate speech detected")
        ]
        pipeline = HardModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertIsNotNone(result.reason)
        self.assertEqual(result.reason.code, "HATE_SPEECH")
        self.assertEqual(result.reason.message, "Hate speech detected")

    def test_should_return_approved_with_empty_steps(self):
        """Return APPROVED with empty steps"""
        # given
        pipeline = HardModerationPipeline([])

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(result.is_rejected)

    def test_should_ignore_multiple_warnings(self):
        """Ignore multiple warnings and return APPROVED"""
        # given
        steps = [
            WarningStep(code="SPAM", message="Spam detected"),
            WarningStep(code="TOO_LONG", message="Message too long"),
            WarningStep(code="BAD_WORDS", message="Bad words detected")
        ]
        pipeline = HardModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(result.is_rejected)
        self.assertEqual(len(result.warnings), 0)

    def test_should_process_steps_until_reason(self):
        """Process steps in order and stop at first reason"""

        # given
        class CounterStep(ModerationStep):
            def __init__(self):
                self.called = False

            async def process(self, text: str):
                self.called = True
                return None

        step1 = CounterStep()
        step2 = RejectStep()
        step3 = CounterStep()

        steps = [step1, step2, step3]
        pipeline = HardModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertTrue(step1.called)
        self.assertFalse(step3.called)
        self.assertEqual(result.verdict, ModerationVerdict.REJECTED)
        self.assertTrue(result.is_rejected)


# ============= TESTS FOR SOFT MODERATION PIPELINE =============

class TestSoftModerationPipeline(unittest.TestCase):
    def setUp(self):
        self.text = "Test message"

    def test_should_return_approved_when_no_issues(self):
        """Return APPROVED when all steps pass"""
        # given
        steps = [PassStep(), PassStep()]
        pipeline = SoftModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(result.is_rejected)
        self.assertEqual(len(result.warnings), 0)

    def test_should_return_warning(self):
        """Return WARNING when step returns ModerationWarning"""
        # given
        steps = [WarningStep()]
        pipeline = SoftModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.WARNING)
        self.assertFalse(result.is_rejected)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0].code, "SPAM")
        self.assertEqual(result.warnings[0].message, "Potential spam detected")

    def test_should_collect_multiple_warnings(self):
        """Collect multiple warnings"""
        # given
        steps = [
            WarningStep(code="SPAM", message="Spam detected"),
            WarningStep(code="TOO_LONG", message="Message too long"),
            WarningStep(code="BAD_WORDS", message="Bad words detected")
        ]
        pipeline = SoftModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.WARNING)
        self.assertEqual(len(result.warnings), 3)
        self.assertEqual(result.warnings[0].code, "SPAM")
        self.assertEqual(result.warnings[0].message, "Spam detected")
        self.assertEqual(result.warnings[1].code, "TOO_LONG")
        self.assertEqual(result.warnings[1].message, "Message too long")
        self.assertEqual(result.warnings[2].code, "BAD_WORDS")
        self.assertEqual(result.warnings[2].message, "Bad words detected")
        self.assertFalse(result.is_rejected)

    def test_should_reject_on_first_reason(self):
        """Reject immediately on ModerationReason"""
        # given
        steps = [
            WarningStep(code="SPAM", message="Spam detected"),
            RejectStep(code="HATE_SPEECH", message="Hate speech detected")
        ]
        pipeline = SoftModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertIsNotNone(result.reason)
        self.assertEqual(result.reason.code, "HATE_SPEECH")
        self.assertEqual(result.reason.message, "Hate speech detected")
        self.assertEqual(len(result.warnings), 0)

    def test_should_return_approved_with_empty_steps(self):
        """Return APPROVED with empty steps"""
        # given
        pipeline = SoftModerationPipeline([])

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(result.is_rejected)

    def test_should_not_collect_warnings_on_rejection(self):
        """Should not collect warnings when rejection occurs"""
        # given
        steps = [
            WarningStep(code="SPAM", message="Spam detected"),
            RejectStep(code="BAN_WORDS", message="Banned word detected"),
            WarningStep(code="TOO_LONG", message="Too long")
        ]
        pipeline = SoftModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertEqual(result.verdict, ModerationVerdict.REJECTED)
        self.assertTrue(result.is_rejected)
        self.assertEqual(len(result.warnings), 0)

    def test_should_process_all_steps_until_reason(self):
        """Process steps in order and stop at first reason"""

        # given
        class CounterStep(ModerationStep):
            def __init__(self):
                self.called = False

            async def process(self, text: str):
                self.called = True
                return None

        step1 = CounterStep()
        step2 = RejectStep()
        step3 = CounterStep()

        steps = [step1, step2, step3]
        pipeline = SoftModerationPipeline(steps)

        # when
        result = asyncio.run(pipeline.validate(self.text))

        # then
        self.assertTrue(step1.called)
        self.assertFalse(step3.called)
        self.assertEqual(result.verdict, ModerationVerdict.REJECTED)
        self.assertTrue(result.is_rejected)


# ============= COMPARISON TESTS =============

class TestSoftVsHardComparison(unittest.TestCase):
    def setUp(self):
        self.text = "Test message"

    def test_soft_collects_warnings_hard_ignores(self):
        """Soft collects warnings, Hard ignores them"""
        # given
        steps = [WarningStep(code="SPAM", message="Spam detected")]

        # when
        soft = SoftModerationPipeline(steps)
        hard = HardModerationPipeline(steps)

        soft_result = asyncio.run(soft.validate(self.text))
        hard_result = asyncio.run(hard.validate(self.text))

        # then
        self.assertEqual(soft_result.verdict, ModerationVerdict.WARNING)
        self.assertEqual(len(soft_result.warnings), 1)
        self.assertEqual(soft_result.warnings[0].code, "SPAM")

        self.assertEqual(hard_result.verdict, ModerationVerdict.APPROVED)
        self.assertEqual(len(hard_result.warnings), 0)

        self.assertFalse(soft_result.is_rejected)
        self.assertFalse(hard_result.is_rejected)

    def test_both_reject_on_reason(self):
        """Both pipelines reject on ModerationReason"""
        # given
        steps = [RejectStep(code="BAN_WORDS", message="Banned word detected")]

        # when
        soft = SoftModerationPipeline(steps)
        hard = HardModerationPipeline(steps)

        soft_result = asyncio.run(soft.validate(self.text))
        hard_result = asyncio.run(hard.validate(self.text))

        # then
        self.assertEqual(soft_result.verdict, ModerationVerdict.REJECTED)
        self.assertEqual(hard_result.verdict, ModerationVerdict.REJECTED)
        self.assertTrue(soft_result.is_rejected)
        self.assertTrue(hard_result.is_rejected)
        self.assertEqual(soft_result.reason.code, "BAN_WORDS")
        self.assertEqual(hard_result.reason.code, "BAN_WORDS")

    def test_both_approve_on_pass(self):
        """Both pipelines return APPROVED when all steps pass"""
        # given
        steps = [PassStep(), PassStep()]

        # when
        soft = SoftModerationPipeline(steps)
        hard = HardModerationPipeline(steps)

        soft_result = asyncio.run(soft.validate(self.text))
        hard_result = asyncio.run(hard.validate(self.text))

        # then
        self.assertEqual(soft_result.verdict, ModerationVerdict.APPROVED)
        self.assertEqual(hard_result.verdict, ModerationVerdict.APPROVED)
        self.assertFalse(soft_result.is_rejected)
        self.assertFalse(hard_result.is_rejected)
        self.assertEqual(len(soft_result.warnings), 0)
        self.assertEqual(len(hard_result.warnings), 0)

    def test_soft_returns_warning_hard_returns_approved_with_mixed_warnings(self):
        """Soft returns WARNING, Hard returns APPROVED when only warnings exist"""
        # given
        steps = [
            WarningStep(code="SPAM", message="Spam detected"),
            PassStep(),
            WarningStep(code="TOO_LONG", message="Message too long")
        ]

        # when
        soft = SoftModerationPipeline(steps)
        hard = HardModerationPipeline(steps)

        soft_result = asyncio.run(soft.validate(self.text))
        hard_result = asyncio.run(hard.validate(self.text))

        # then
        self.assertEqual(soft_result.verdict, ModerationVerdict.WARNING)
        self.assertEqual(len(soft_result.warnings), 2)

        self.assertEqual(hard_result.verdict, ModerationVerdict.APPROVED)
        self.assertEqual(len(hard_result.warnings), 0)

        self.assertFalse(soft_result.is_rejected)
        self.assertFalse(hard_result.is_rejected)


if __name__ == "__main__":
    unittest.main()