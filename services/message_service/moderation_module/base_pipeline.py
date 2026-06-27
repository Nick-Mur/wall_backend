from .step import ModerationStep


class BaseModerationPipline:
    def __init__(self, steps: list[ModerationStep]):
        self.steps = steps
