from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
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
import re       # to find an AI answer


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
# it's the plain text, Langchain works with object
system_prompt = (
    "You are a Senior AML Analyst. Analyze the provided data "
    "and return your findings strictly in the requested format."
)

# Langchain works with this object, not plain str
system_message = SystemMessage(content=system_prompt)


def _create_aml_agent(db_session: Session):
    """
    Creates a fully ready-to-use Engine,
    which consists of llm agent, tools, and conversational framework.
    Provides a safe db Session to our outer fuctions in tools
    and gets the tools.
    """

    # create the brain, temprature = 0 removes randomness
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)

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

    # LLM does not undestand Python dict, so we convert it to JSON string
    # get the JSON schema
    schema_dict = AMLAnalysisSchema.model_json_schema()
    schema_json_string = json.dumps(schema_dict, indent=2)  # dump a dict to string JSON

    # escape the curly braces so LangChain doesn't get confused
    # Langchain uses those brackets{} for his own vars, so we just double them
    escaped_schema = schema_json_string.replace("{", "{{").replace("}", "}}")

    # everything in a prompt should be string, no dict and schemas
    # creating the strict conversational framework that AI must follow
    prompt = ChatPromptTemplate.from_messages([
        # 1. The Persona & Rules (with explicit escaped JSON schema injected)
        ("system", system_prompt + f"\nEnsure your final answer is strictly in JSON format matching this schema:\n{escaped_schema}"),

        # 2. The User Input
        ("human", "{input}"),

        # 3. The Required Working Space
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # binds llm, tools and prompt into single logical unit
    # llm - brain, my_tools - hands, prompt - instructions
    agent = create_tool_calling_agent(llm, my_tools, prompt)    # decision-making brain

    # full engine with loops, memory handling, etc.
    agent_executor = AgentExecutor(agent=agent, tools=my_tools, verbose=True)

    return agent_executor


def run_agent(db: Session, question: str) -> dict:
    """
    Executes the AML agent to analyze a specific compliance question.
    Saves the result to the database for auditing and returns the final output.
    """
    agent_executor = _create_aml_agent(db_session=db)

    # LangChain's trigger expects a dict matching the prompt placeholder
    history_of_execution = agent_executor.invoke({"input": question})

    #  get the raw output from the agent
    raw_output = history_of_execution["output"]

    #  anthropic sometimes returns a list of blocks. if so, extract the text string.
    if isinstance(raw_output, list):
        raw_output = raw_output[0].get("text", str(raw_output))

    #  use regex to find only the JSON block, ignoring conversational text
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_output, re.DOTALL)
    if match:
        clean_json_string = match.group(1)  # gives only the JSON part
    else:
        # fallback in case the ai didn't use markdown backticks
        clean_json_string = raw_output

    # now safely parse the clean string into a dictionary
    try:
        ai_data = json.loads(clean_json_string)
    except json.JSONDecodeError:
        # failsafe just in case the AI hallucinates bad JSON
        ai_data = {"summary": clean_json_string, "analysis_type": "general"}

    # save the summary string to the database
    create_ai_summary_report(db=db, data={
        "summary": ai_data.get("summary", clean_json_string),
        "type": ai_data.get("analysis_type", "general"),
        "report_id": None  # None unless we are targeting a specific transaction
    })

    return ai_data
