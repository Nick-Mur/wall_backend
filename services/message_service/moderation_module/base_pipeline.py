# TODO: Реализовать базовый pipeline модерации.
from typing import List
from .step import ModerationStep


class BaseModerationPipline:
    def __init__(self, steps: List[ModerationStep]):
        self.steps = steps
