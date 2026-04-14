from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from sqlalchemy.orm import Session
from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.tools import (
    get_structuring_tool,
    get_all_raw_data_tool,
    get_geographical_inflow_tool,
    get_high_velocity_transfers_tool,
    get_unverified_originators_tool,
    get_whole_professional_summary_tool
)
from app.db.repository import create_ai_summary_report
from typing import Literal
import json


# defines the shape of the ai answer, makes it more structured
class AMLAnalysisSchema(BaseModel):
    """
    Represents the structured output of an AML investigation.

    Fields like 'risk_score' and 'reasoning' are not persisted in the database,
    but are required to force the agent into a 'Chain of Thought' process.
    This improves the accuracy and depth of the final 'summary' field.
    """
    summary: str = Field(description="A professional 3-sentence narrative for compliance officers.")
    risk_score: int = Field(description="Risk level from 1-10.")
    reasoning: str = Field(description="Internal logic for the score (not for the final report).")

    # forces AI to categorize its own raport
    analysis_type: Literal["structuring", "geographical_inflow", "high_velocity", "unverified_originator", "general"] = Field(
        description="Categorize the type of investigation based on the user's request."
    )


# it's like the job message, describes what to do
system_promt = (
    "You are a Senior AML Analyst. Analyze the provided data "
    "and return your findings strictly in the requested format."
)

system_message = SystemMessage(content=system_promt)


def _create_aml_agent(db_session: Session):
    """
    Creates a fully ready-to-use Engine,
    which consists of llm agent, tools, and conversational framework.
    Provides a safe db Session to our outer fuctions in tools
    and gets the tools.
    """

    # temprature = 0 removes randomness
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)

    structuring_tool = get_structuring_tool(db_session)
    geographical_inflow_tool = get_geographical_inflow_tool(db_session)
    unverified_originators_tool = get_unverified_originators_tool(db_session)
    high_velocity_transfers_tool = get_high_velocity_transfers_tool(db_session)
    raw_data_tool = get_all_raw_data_tool(db_session)
    whole_professional_summary_tool = get_whole_professional_summary_tool(db_session)

    my_tools = [
        structuring_tool,
        geographical_inflow_tool,
        unverified_originators_tool,
        high_velocity_transfers_tool,
        raw_data_tool,
        whole_professional_summary_tool
    ]

    # creating the strcit conversational framework that AI must follow
    prompt = ChatPromptTemplate.from_messages([
        # 1. The Persona & Rules (with explicit JSON schema instruction)
        ("system", system_promt + "\nEnsure your final answer is strictly in JSON format matching the defined AMLAnalysisSchema."),

        # 2. The User Input
        ("human", "{input}"),

        # 3. The Required Working Space
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # binds llm, tools and prompt into single logical unit
    agent = create_tool_calling_agent(llm, my_tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=my_tools, verbose=True)

    return agent_executor


def run_agent(db: Session, question: str):
    """
    Executes the AML agent to analyze a specific compliance question.
    Saves the result to the database for auditing and returns the final output.
    """
    agent_executor = _create_aml_agent(db_session=db)

    # LangChain's trigger expects a dict matching the prompt placeholder
    history_of_execution = agent_executor.invoke({"input": question})

    # AgentExecutor returns a dict — the answer is always in "output" key as a string
    final_analysis_string = history_of_execution["output"]

    try:
        ai_data = json.loads(final_analysis_string)
    except json.JSONDecodeError:
        # Failsafe just in case the AI hallucinates bad JSON
        ai_data = {"summary": final_analysis_string, "analysis_type": "general"}

    # Save the summary string to the database
    create_ai_summary_report(db=db, data={
        "summary": ai_data.get("summary", final_analysis_string),
        "type": ai_data.get("analysis_type", "general"),
        "report_id": None  # None unless we are targeting a specific transaction
    })

    return ai_data
