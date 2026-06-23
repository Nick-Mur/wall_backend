import unittest
from uuid import uuid4
from unittest.mock import Mock, patch

from services.message_service.domain.message import Message
from services.message_service.application.visibility import VisibilityError, hide_message, erase_message, detach_message


class TestHideMessage(unittest.TestCase):
    def test_should_call_hide_on_message(self):
        """Should call hide method on message"""
        # given
        message = Message.create(text="Hello!")

        # when
        hide_message(message)

        # then
        self.assertFalse(message.is_visible)

    def test_should_raise_error_if_message_is_None(self):
        """Should raise error when message is None"""
        # given
        message = None

        def action():
            # when
            hide_message(message)

        # then
        self.assertRaises(AttributeError, action)

    def test_should_raise_visibility_error_if_already_hidden(self):
        """Should raise VisibilityError if message is already hidden"""
        # given
        message = Message.create(text="Hello!")
        message.hide()

        def action():
            # when
            hide_message(message)

        # then
        self.assertRaises(VisibilityError, action)


class TestDetachMessage(unittest.TestCase):
    """Tests for detach_message() function"""

    def test_should_call_detach_on_message(self):
        """Should call detach method on message"""
        # given
        author_id = uuid4()
        message = Message.create(text="Hello!", author_id=author_id)

        # when
        detach_message(message)

        # then
        self.assertIsNone(message.author_id)

    def test_should_handle_message_without_author(self):
        """Should handle message without author"""
        # given
        message = Message.create(text="Hello!")

        # when
        detach_message(message)

        # then
        self.assertIsNone(message.author_id)  # remains None

    def test_should_raise_error_if_message_is_None(self):
        """Should raise error when message is None"""
        # given
        message = None

        def action():
            # when
            detach_message(message)

        # then
        self.assertRaises(AttributeError, action)


class TestEraseMessage(unittest.TestCase):
    def test_should_call_erase_on_message(self):
        """Should call erase method on message"""
        # given
        author_id = uuid4()
        message = Message.create(text="Hello!", author_id=author_id)

        # when
        erase_message(message)

        # then
        self.assertTrue(message.hidden)
        self.assertIsNone(message.author_id)

    def test_should_erase_already_hidden_message(self):
        """Should erase already hidden message"""
        # given
        message = Message.create(text="Hello!")
        message.hide()

        # when
        erase_message(message)

        # then
        self.assertTrue(message.hidden)

    def test_should_raise_error_if_message_is_None(self):
        """Should raise error when message is None"""
        # given
        message = None

        def action():
            # when
            erase_message(message)

        # then
        self.assertRaises(AttributeError, action)


class TestVisibilityError(unittest.TestCase):
    """Tests for VisibilityError custom exception"""

    def test_should_inherit_from_ValueError(self):
        """VisibilityError should inherit from ValueError"""
        # then
        self.assertTrue(issubclass(VisibilityError, ValueError))

    def test_should_store_error_message(self):
        """Should store error message"""
        # given
        error_message = "Cannot hide message that is already hidden"

        # when
        with self.assertRaises(VisibilityError) as context:
            raise VisibilityError(error_message)

        # then
        self.assertEqual(str(context.exception), error_message)

    def test_should_work_without_message(self):
        """Should work without error message"""
        # when
        with self.assertRaises(VisibilityError) as context:
            raise VisibilityError()

        # then
        self.assertEqual(str(context.exception), "")


class TestMessageActionsIntegration(unittest.TestCase):
    def test_should_hide_then_erase_message(self):
        """Should hide and then erase message"""
        # given
        message = Message.create(text="Secret content", author_id=uuid4())

        # when
        hide_message(message)
        erase_message(message)

        # then
        self.assertTrue(message.hidden)
        self.assertIsNone(message.author_id)

    def test_should_detach_then_hide_message(self):
        """Should detach author and then hide message"""
        # given
        message = Message.create(text="Hello!", author_id=uuid4())

        # when
        detach_message(message)
        hide_message(message)

        # then
        self.assertIsNone(message.author_id)
        self.assertFalse(message.is_visible)


if __name__ == "__main__":
    unittest.main()
