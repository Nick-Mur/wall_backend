from dataclasses import dataclass, field

from services.message_service.domain.moderation import (
    ModerationReason,
    ModerationVerdict,
    ModerationWarning,
)


@dataclass
class ModerationResult:
    verdict: ModerationVerdict = ModerationVerdict.APPROVED
    reason: ModerationReason | None = None
    warnings: list[ModerationWarning] = field(default_factory=list)

    @property
    def is_rejected(self) -> bool:
        return self.verdict == ModerationVerdict.REJECTED
