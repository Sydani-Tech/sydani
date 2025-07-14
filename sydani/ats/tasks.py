from crewai import Task
from textwrap import dedent
from pydantic import BaseModel

class OutputModel(BaseModel):
  name: str
  status: str 
  score: int
  reason: str

def cv_screen(agent, cv_content, criteria):

  return  Task(
    description=f""" 
      Task: Conduct a thorough analysis of cv_content to determine its alignment with the job_criteria. Your primary focus should be on the experience, technical skills, and professional competencies, and their relevance to the job_criteria. Disregard soft skills for this analysis.
      Assign a rating score between 0 and 100 to evaluate the cv_content suitability for the job_criteria. A score of 85 to 100 indicates that the cv_content is qualified, while a score below 60 indicates it is unqualified. Ensure strict adherence to these guidelines during the analysis.

      Inputs:

      - cv_content: {cv_content}.
      - job_criteria: {criteria}.                 

      Outputs:
      You must return a JSON string with these keys:
      name, status, score and reason
      - name: Applicant's name (from CV).
      - status: Indicates if applicant is "qualified" or "unqualified":
          - "qualified": If CV meets all requirements.
          - "unqualified": If CV does not meet all requirements. 
      - score: Rate the canditate from 1 to 100 by assessing numerically the number of required competencies against what is available on the cv. give more weight to requirements that are stated as mandatory.
      - reason: Explain in detail your evaluation of the cv. escape string for python use.

      Important Notes:

      - Function must return a json data. 
      - You must provide summarized reason for qualification or disqualification in `reason`.
      - Reason must be one line escaped string dont break the text. For each point in the reason you must indicate end of point with this sign ' -> ' 
    """,
    expected_output="""
    JSON data like: 
        {
          "name":"applicant name", 
          "status": "qualified or unqualified",
          "score":  "cv score 1 to 100",
          "reason": "summarized  reason"
        }
    """,
    output_json=OutputModel,
    async_execution=False,
    agent=agent,
  )

def research_task(topic, tools, researcher): 
  return Task(
    description=f"""Identify the next big trend in {topic}.
    Focus on identifying pros and cons and the overall narrative.
    Your final report should clearly articulate the key points,
    its market opportunities, and potential risks.""",
    expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
    tools=tools,
    agent=researcher,
  )

def write_task(topic, tools, writer):
  return Task(
    description=f"""Compose an insightful article on {topic}.
    Focus on the latest trends and how it's impacting the industry.
    This article should be easy to understand, engaging, and positive.""",
    expected_output=f'A 4 paragraph article on {topic} advancements fromated as markdown.',
    tools=tools,
    agent=writer,
    async_execution=False,
    output_file=f"{topic}-blog-post.md"  # Example of output customization
  )