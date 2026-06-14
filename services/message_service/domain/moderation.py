# TODO: Описать доменные типы модерации: verdict, warning, reason.
from enum import Enum


class ModerationVerdict(str, Enum):
    APPROVED = "approved"
    WARNING = "warning"
    REJECTED = "rejected"

class ModerationWarning:
    code : str
    message : str

    def to_message(self) -> str:
        return self.message
class ModerationReason:
    code : str
    message : str

    def to_message(self) -> str:
        return self.message
