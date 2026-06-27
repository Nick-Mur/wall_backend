"""Создание шагов по строковому названию"""

from .step import ModerationStep
from .steps.ban_words import BanWordsStep
from .steps.pii import PIIStep
from .steps.normalization import NormalizationStep


class RegistryStep:
    _steps: dict[str, type[ModerationStep]] = {
        "ban_words": BanWordsStep,
        "pii": PIIStep,
        "normalization": NormalizationStep,
    }

    @classmethod
    def create_step(cls, name: str, **kwargs):
        step_class = cls._steps.get(name)
        if not step_class:
            raise ValueError(f"Unknown step: {name}")
        return step_class(**kwargs)
