# TODO: Реализовать шаг normalization.
import re

from services.message_service.moderation_module.step import ModerationStep
from services.message_service.domain.moderation import ModerationWarning

MAX_SPACES_SEQUENCE = 3
MAX_NEWLINES_SEQUENCE = 3


class NormalizationStep(ModerationStep):
    def process(self, text: str) -> ModerationWarning | None:
        if not text:
            return None
        space_reg = rf'[ \t]{{{MAX_SPACES_SEQUENCE + 1},}}'
        if re.search(space_reg, text):
            return ModerationWarning(code="SPACES", message=f"Text has a lot of spaces")
        newline_reg = rf'\n{{{MAX_NEWLINES_SEQUENCE + 1},}}'
        if re.search(newline_reg, text):
            return ModerationWarning(
                code="NEWLINES",
                message="Text has a lot of newlines"
            )
        if text.startswith(' ') or text.endswith(' '):
            return ModerationWarning(code="SPACES", message="There are leading or trailing whitespaces")
        return None
