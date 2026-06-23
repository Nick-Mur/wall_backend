# TODO: Реализовать сценарии hide, detach, erase.
from services.message_service.domain.message import Message

class VisibilityError(ValueError):
    pass

def hide_message(message: Message) -> None:
    if not message.is_visible:
        raise VisibilityError("Message is already hidden")
    message.hide()

def detach_message(message: Message) -> None:
    message.detach()

def erase_message(message: Message) -> None:
    message.erase()
