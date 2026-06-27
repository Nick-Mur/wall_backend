from .base_pipeline import BaseModerationPipeline
from .moderation_result import ModerationResult
from ..domain.moderation import ModerationVerdict, ModerationReason, ModerationWarning


class HardModerationPipeline(BaseModerationPipeline):
    async def validate(self, text: str) -> ModerationResult:
        for step in self.steps:
            result = await step.process(text)
            if isinstance(result, ModerationReason):
                return ModerationResult(
                    verdict=ModerationVerdict.REJECTED,
                    reason=result
                )
        return ModerationResult(verdict=ModerationVerdict.APPROVED)


class SoftModerationPipeline(BaseModerationPipeline):
    async def validate(self, text: str) -> ModerationResult:
        warnings = []
        for step in self.steps:
            result = await step.process(text)
            if isinstance(result, ModerationReason):
                return ModerationResult(
                    verdict=ModerationVerdict.REJECTED,
                    reason=result
                )
            if isinstance(result, ModerationWarning):
                warnings.append(result)

        if warnings:
            return ModerationResult(
                verdict=ModerationVerdict.WARNING,
                warnings=warnings
            )

        return ModerationResult(verdict=ModerationVerdict.APPROVED)
