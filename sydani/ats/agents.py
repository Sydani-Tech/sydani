from dotenv import load_dotenv
from crewai import Agent

from langchain_openai import ChatOpenAI

import os


load_dotenv()

OpenAIGPT35 = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

def application_screening_expert():
    return Agent(
        role="Application Screening Expert",
        goal="Efficiently screen job applicant CV",
        verbose=False,
        memory=False,
        cache=False,
        backstory="""Conduct a thorough analysis of cv_content to determine its alignment with the job_criteria. 
        Your primary focus should be on the experience, technical skills, and professional competencies, and their relevance to the job_criteria. 
        Disregard soft skills for this analysis. Assign a rating score between 0 and 100 to evaluate the cv_content suitability for the job_criteria. 
        A score of 70 to 100 indicates that the cv_content is qualified, while a score below 70 indicates it is unqualified. Ensure to reduce the score of the applicant for every job_criteria the cv_content lacks. If the candidate lacks a mandatory job_criteria, disqualify that candidate.
        Ensure strict adherence to these guidelines during the analysis""",
        
        llm=OpenAIGPT35,
    )


def researcher(topic, tools):

    return Agent(
        role="Senior Researcher",
        goal=f"Uncover groundbreaking technologies in {topic}",
        memory=True,
        backstory="""Driven by curiosity, you're at the forefront of
    innovation, eager to explore and share knowledge that could change
    the world.""",
        tools=tools,
        allow_delegation=True,
        llm=OpenAIGPT35,
    )


# Creating a writer agent with custom tools and delegation capability
def writer(topic, tools):

    return Agent(
        role="Writer",
        goal=f"Narrate compelling tech stories about {topic}",
        verbose=True,
        memory=True,
        backstory="""With a flair for simplifying complex topics, you craft
    engaging narratives that captivate and educate, bringing new
    discoveries to light in an accessible manner.""",
        tools=tools,
        allow_delegation=False,
        llm=OpenAIGPT35,
    )
