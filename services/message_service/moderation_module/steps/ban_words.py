from services.message_service.moderation_module.step import ModerationStep
from services.message_service.domain.moderation import ModerationReason


class BanWordsStep(ModerationStep):
    def __init__(self, forbidden_words: list[str]):
        self.forbidden_words = forbidden_words

    async def process(self, text: str) -> ModerationReason | None:
        low_text = text.lower()
        for word in self.forbidden_words:
            if word in low_text:
                return ModerationReason(
                    code="BAN_WORDS",
                    message=f"Banned word detected: {word}"
                )
        return None
