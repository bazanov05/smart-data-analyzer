from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage


# defines the shape of the ai answer, makes it more structured
class AMLAnalysisSchema(BaseModel):
    """
    Represents the structured output of an Anti-Money Laundering (AML)
    investigation.
    """
    summary: str = Field(description="A professional 3-sentence narrative for compliance officers.")
    risk_score: int = Field(description="Risk level from 1-10.")
    reasoning: str = Field(description="Internal logic for the score (not for the final report).")


# it's like the job message, describes what to do
system_promt = (
    "You are a Senior AML Analyst. Analyze the provided data "
    "and return your findings strictly in the requested format."
)

system_message = SystemMessage(content=system_promt)
