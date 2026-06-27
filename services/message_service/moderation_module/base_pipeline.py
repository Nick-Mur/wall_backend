from .step import ModerationStep


class BaseModerationPipeline:
    def __init__(self, steps: list[ModerationStep]):
        self.steps = steps
