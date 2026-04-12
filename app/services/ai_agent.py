from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from sqlalchemy.orm import Session
from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import (
    get_structuring_tool,
    get_all_raw_data_tool,
    get_geographical_inflow_tool,
    get_high_velocity_transfers_tool,
    get_unverified_originators_tool
)


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


def create_aml_agent(db_session: Session):
    """
    Creates a fully ready-to-use Engine,
    which consists of llm agent, tools, and conversational framework.
    Provides a safe db Session to our outer fuctions in tools
    and gets the tools.
    """

    # temprature = 0 removes randomness
    model_object = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
    my_tools = []

    structuring_tool = get_structuring_tool(db_session)
    geographical_inflow_tool = get_geographical_inflow_tool(db_session)
    unverified_originators_tool = get_unverified_originators_tool(db_session)
    high_velocity_transfers_tool = get_high_velocity_transfers_tool(db_session)
    raw_data_tool = get_all_raw_data_tool(db_session)

    my_tools = [
        structuring_tool,
        geographical_inflow_tool,
        unverified_originators_tool,
        high_velocity_transfers_tool,
        raw_data_tool
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
    agent = create_tool_calling_agent(model_object, my_tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=my_tools, verbose=True)

    return agent_executor
