from pydantic import BaseModel, Field


class AMLAnalysisSchema(BaseModel):
    """
    Represents the structured output of an Anti-Money Laundering (AML)
    investigation, capturing the high-level findings,
    risk level, and supporting evidence.
    """

    summary: str = Field(
        description="A professional 3-sentence narrative "
        "for compliance officers."
        )
    risk_score: int = Field(description="Risk level from 1-10.")
    reasoning: str = Field(
        description="Internal logic for the score "
        "(not for the final report)."
        )
