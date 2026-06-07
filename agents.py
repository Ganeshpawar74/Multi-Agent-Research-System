# agents.py This is the heart of the project. We will build 4 things here. First the Search Agent using create_react_agent + AgentExecutor which will use the web_search tool. Second the Reader Agent using the same pattern but with the scrape_url tool. Third the Writer Chain using the modern LCEL pipe syntax — prompt | llm | StrOutputParser() which takes all the research and writes a full report. Fourth the Critic Chain again using LCEL pipe which reads the report and gives a score and feedback.

import os
from rich import print
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_mistralai import ChatMistralAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url

load_dotenv()

# model setup
llm = ChatMistralAI(
    model="ministral-8b-latest",
    temperature=0
)
# 1st agent - Search Agent - fetchfrom Tavily API
def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )

# 2nd agent - Reader Agent - fetch from BeautifulSoup
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )
        
# writer chain - takes all the research and writes a full report

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. Write clear, structured and insightful reports."
    ),
    (
        "human",
        """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic chain - reads the report and gives a score and feedback
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. Be honest and specific."
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
"""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()
