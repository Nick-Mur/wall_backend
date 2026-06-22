import unittest
from services.message_service.domain.moderation import (ModerationVerdict, ModerationWarning, ModerationReason)

class TestModerationVerdict(unittest.TestCase):
    def test_should_have_correct_value(self):
        """Checking verdict values"""
        self.assertEqual(ModerationVerdict.APPROVED, "approved")
        self.assertEqual(ModerationVerdict.WARNING, "warning")
        self.assertEqual(ModerationVerdict.REJECTED, "rejected")

class TestModerationReason(unittest.TestCase):
    def test_should_create_reason(self):
        """Creating Reasons"""
        # given
        code = "HATE_SPEECH"
        message = "Hate speech is prohibited"

        # when
        reason = ModerationReason(code=code, message=message)

        # then
        self.assertEqual(reason.code, code)
        self.assertEqual(reason.message, message)

    def test_should_return_message(self):
        """Returning text"""
        # given
        reason = ModerationReason(code="SPAM", message="SPAM is prohibited")

        # when
        result = reason.to_message()

        # then
        self.assertEqual(result, "SPAM is prohibited")



if __name__ == "__main__":
    unittest.main()