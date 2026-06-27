# TODO: Описать доменные типы модерации: verdict, warning, reason.
from enum import Enum
from dataclasses import dataclass


class ModerationVerdict(str, Enum):
    APPROVED = "approved"
    WARNING = "warning"
    REJECTED = "rejected"


@dataclass
class ModerationWarning:
    code: str
    message: str


@dataclass
class ModerationReason:
    code: str
    message: str
