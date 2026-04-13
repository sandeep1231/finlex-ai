from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.ai.tools import get_all_tools
from app.ai.prompts.accounting import ACCOUNTING_SYSTEM_PROMPT
from app.ai.prompts.legal import LEGAL_SYSTEM_PROMPT
from app.config import get_settings

settings = get_settings()

GENERAL_SYSTEM_PROMPT = """You are FinLex AI, an expert AI assistant specializing in Indian Accounting and Law.
You help Chartered Accountants, Lawyers, Accountants, and other professionals with:

1. **Tax Queries**: Income tax, GST, TDS, capital gains, tax planning under Indian tax laws
2. **Legal Queries**: Contract review, compliance, legal drafting, Indian legal framework
3. **Calculations**: Tax computation, GST calculation, TDS computation, financial ratios
4. **Document Drafting**: Contracts, legal notices, engagement letters, board resolutions
5. **Research**: Tax provisions, case law references, regulatory updates
6. **Compliance**: Due dates, filing requirements, regulatory deadlines

**IMPORTANT RULES:**
- Always reference the specific section/provision of Indian law when applicable
- Clearly distinguish between the Old and New Tax Regime when discussing income tax
- Use the latest tax rates for FY 2025-26 (AY 2026-27) unless asked otherwise
- For GST, use the post-GST 2.0 rates effective from September 22, 2025
- Always add a disclaimer that this is AI-generated and should be verified by a qualified professional
- Never fabricate case law citations or section numbers
- When unsure, clearly state so rather than guessing
- All amounts are in Indian Rupees (₹) unless specified otherwise

**Context from knowledge base:**
{context}
"""

MODE_PROMPTS = {
    "accounting": ACCOUNTING_SYSTEM_PROMPT,
    "legal": LEGAL_SYSTEM_PROMPT,
    "general": GENERAL_SYSTEM_PROMPT,
}


def get_llm():
    """Get the LLM based on configuration."""
    if settings.llm_provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.google_model,
            google_api_key=settings.google_api_key,
            temperature=0.1,
            max_output_tokens=4096,
        )
    elif settings.llm_provider == "openai":
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.1,
            max_tokens=4096,
        )
    else:
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.1,
        )


def create_agent(mode: str = "general") -> AgentExecutor:
    """Create a LangChain agent with tools for the specified mode."""
    llm = get_llm()
    tools = get_all_tools()

    system_prompt = MODE_PROMPTS.get(mode, GENERAL_SYSTEM_PROMPT)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.debug,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
