# TODO: Реализовать шаг проверки запрещённых слов.
from services.message_service.moderation_module.step import ModerationStep


class BanWordsStep(ModerationStep):
    def __init__(self, forbidden_words: list):
        self.forbidden_words = forbidden_words

    async def process(self, text: str) -> str | None:
        low_text = text.lower()
        for word in self.forbidden_words:
            if word in low_text:
                return f"Banned word detected: {word}"
        return None
