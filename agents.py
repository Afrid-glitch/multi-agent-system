from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model ="openai/gpt-oss-120b", temperature=0)


def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

writer_prompt =ChatPromptTemplate.from_messages([
    ("system", "You are a expert research writer. write clear, structured and insightfill report "),
    ("human","""Write a detailed research report on the topic below.
Topic: {topic}

Research Gathered:
{research}

Structure the report as:
-Intropduction
-Key Findings (minimum 3 well-explained points)
-conclusion
-Sources (list all sources used in the research)

Be detailed, factual and professional.""")

])

writer_chain =  writer_prompt | llm | StrOutputParser()

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Sharp and constructive research critic . Be honest and specific "),
    ("human", """Review Review the research report below and evaluate it strictly.messages
Report: {report}

Respond in this exact format:

Score: X/10

Strengths:
-...
-...

Area to improve:
-...
-...

One line verdict:
.....   """)
])

critic_chain =  critic_prompt |llm | StrOutputParser()