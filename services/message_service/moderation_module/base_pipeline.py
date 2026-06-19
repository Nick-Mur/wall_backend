# TODO: Реализовать базовый pipeline модерации.
from typing import List
from .step import ModerationStep
class BasePipeline:
    def __init__(self, steps: List[ModerationStep]):
        self.steps = steps

