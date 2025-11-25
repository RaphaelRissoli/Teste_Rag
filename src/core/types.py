from dataclasses import dataclass
from typing import List, Optional
from src.api.schemas import Citation, Metrics, GuardrailStatus

@dataclass
class QAResult:
    answer: Optional[str]
    citations: List[Citation]
    metrics: Metrics
    guardrail_status: GuardrailStatus

