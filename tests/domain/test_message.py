import unittest
from uuid import uuid4

from services.message_service.domain.message import (Message, MAX_TEXT_LENGTH, MAX_REFERENCES_COUNT)
from services.message_service.domain.exceptions.text_validation_error import TextValidationError
from services.message_service.domain.exceptions.references_validation_error import ReferencesValidationError


class TestMessage(unittest.TestCase):
    def test_should_create_Message(self):
        """Create Message"""
        # given
        text = "My first post"

        # when
        result = Message.create(text=text)

        # then
        self.assertEqual(result.text, text)
        self.assertFalse(result.hidden)
        self.assertEqual(result.references, [])
        self.assertIsNone(result.author_id)
        self.assertIsNotNone(result.id)

    def test_should_trim_text(self):
        """Removing spaces"""
        # given
        text = "    Itmo     "

        # when
        result = Message.create(text)

        # then
        self.assertEqual(result.text, "Itmo")

    def test_should_raise_invalidation_error_if_text_empty(self):
        """Raising an error when text is empty"""
        # given
        text = " "

        def action():
            # when
            Message.create(
                text=text
            )

        # then
        self.assertRaises(
            TextValidationError,
            action
        )

    def test_should_raise_invalidation_error_if_text_too_long(self):
        """Raising an error when text is too long"""
        # given
        text = "AAA" * (MAX_TEXT_LENGTH)

        def action():
            # when
            Message.create(text=text)

        # then
        self.assertRaises(TextValidationError, action)

    def test_should_store_author(self):
        """Saving the author"""
        # given
        author_id = uuid4()
        text = "The second St. Petersburg systems programming meetup. Three scientific and engineering talks on systems programming are planned for students and engineers from St. Petersburg companies."

        # when
        result = Message.create(text=text, author_id=author_id)

        # then
        self.assertEqual(result.author_id, author_id)

    def test_should_store_references(self):
        """Saving references"""
        # given
        references = [uuid4(), uuid4(), uuid4()]
        text = "Hello!"

        # when
        result = Message.create(text=text, references=references)

        # then
        self.assertEqual(result.references, references)

    def test_should_remove_duplicate_references(self):
        """Removing duplicates"""
        # given
        reference = uuid4()
        text = "Hello!"

        # when
        result = Message.create(text=text, references=[reference, reference, reference])

        # then
        self.assertEqual(result.references, [reference])

    def test_should_raise_references_validation_error_if_limit_exceeded(self):
        """Raising an error when references is too many"""
        # given
        references = [uuid4() for i in range(MAX_REFERENCES_COUNT + 1)]
        text = "Hello!"

        def action():
            # when
            Message.create(text=text, references=references)

        # then
        self.assertRaises(ReferencesValidationError, action)

    def test_should_raise_references_validation_error_if_reference_not_uuid(self):
        """Raising an error when reference is not uuid"""
        # given
        reference = ['CrazyFrog_uuid']
        text = "Crazyyyy Froggg"

        def action():
            # when
            Message.create(text=text, references=reference)

        # then
        self.assertRaises(ReferencesValidationError, action)

    def test_should_hide_message(self):
        """hidden message"""
        # given
        message = Message.create(text="Hello!")

        # when
        message.hide()

        # then
        self.assertFalse(message.is_visible)

    def test_should_detach_author(self):
        """Detaching an author"""
        # given
        message = Message.create(text="Hello!", author_id=uuid4())

        # when
        message.detach()

        # then
        self.assertIsNone(message.author_id)

    def test_should_erase_message(self):
        """Erasing message"""
        # given
        message = Message.create(text="Hello!", author_id=uuid4())

        # when
        message.erase()

        # then
        self.assertTrue(message.hidden)
        self.assertIsNone(message.author_id)


if __name__ == "__main__":
    unittest.main()
