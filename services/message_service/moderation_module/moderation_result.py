# TODO: Описать результат модерации.
from dataclasses import dataclass, field
from typing import List, Optional
from services.message_service.domain.moderation import ModerationVerdict, ModerationWarning, ModerationReason

@dataclass
class ModerationResult:
    verdict: ModerationVerdict = ModerationVerdict.APPROVED
    reason: Optional[ModerationReason] = None
    warnings: List[ModerationWarning] = field(default_factory=list)

    @property
    def is_rejected(self) -> bool:
        return self.verdict == ModerationVerdict.REJECTED


