from ..types import MatchResult, MatchDecision

def apply_thresholds(score: float, hard_threshold: float, soft_threshold: float) -> MatchResult:
    if score is None:
        return MatchResult(idx=None, score=None, status=MatchDecision.NONE)
    if score >= hard_threshold:
        return MatchResult(idx=None, score=score, status=MatchDecision.HARD)
    if score >= soft_threshold:
        return MatchResult(idx=None, score=score, status=MatchDecision.SOFT)
    return MatchResult(idx=None, score=score, status=MatchDecision.REJECT)
