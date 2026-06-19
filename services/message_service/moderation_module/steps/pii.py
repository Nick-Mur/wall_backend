# TODO: Реализовать шаг поиска персональных данных.
import re
from services.message_service.moderation_module.step import ModerationStep
from services.message_service.domain.moderation import ModerationWarning


class PIIStep(ModerationStep):
    TEL_REG = r"(\+7|8|7)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
    EMAIL_REG = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    async def process(self, text: str):
        if re.search(self.TEL_REG, text):
            return ModerationWarning(code="PII_PHONE", message="Phone number is detected")
        if re.search(self.EMAIL_REG, text):
            return ModerationWarning(code="PII_EMAIL", message="Email is detected")
        return None
