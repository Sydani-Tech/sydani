import json
from typing import Union
from fastapi import APIRouter, FastAPI, Response
from pydantic import BaseModel
from crewai import Crew, Process
from agents import application_screening_expert
from tasks import cv_screen
from tools import cv_loader
import time
import asyncio
import tiktoken

# Explicitly specify the tokenizer for gpt-4o-mini
tokenizer = tiktoken.get_encoding("cl100k_base")
prefix_router = APIRouter(prefix="/ai/api")

app = FastAPI()

class CVData(BaseModel):
    cv_url: str
    criteria: str 
    additional_info: str

@prefix_router.get("/")
def index():
   return {"code": 200, "status": "Ok"}

@prefix_router.post("/screen")
async def screen_cv(data: CVData):
  cv_url = data.cv_url
  criteria = data.criteria
  additional_info = data.additional_info
  
  # agents = ApplicationTrackingAgents()
  # tasks = ApplicationTrackingTasks()

  cv_content = cv_loader(file_url=cv_url)
  if not cv_content:
    return None
  cv_content = f"{additional_info} {cv_content}"
  screening_agent = application_screening_expert()

  screening_task = cv_screen(
     agent=screening_agent, 
     cv_content=cv_content, 
     criteria=criteria
  )

  crew = Crew(
    agents=[screening_agent],
    tasks=[screening_task],
    process=Process.sequential,
    verbose=False,
  )

  try:
      result = await asyncio.to_thread(crew.kickoff)
        # return result
      # result = crew.kickoff()
      print('Crew kickoff completed.')
      print('Result:', str(result))
      return result
      # task_result = screening_task.result if hasattr(screening_task, 'result') else None
      # print('Task Result:', task_result)
  except Exception as e:
      print('An error occurred during crew kickoff:', e)
 

  # return Response(content=f"""{result}""", media_type="application/json")

# Research endpoint -> Never mind this endpoint is just for testing---------
# @prefix_router.get("/write/{topic}")
# def task_agent(topic: str):
#   pass
#   # print(topic)
#   # from langchain_community.tools import DuckDuckGoSearchRun
#   # # from tools import ResearchTools
#   # from agents import researcher, writer
#   # from tasks import research_task, write_task

#   # search_tool = DuckDuckGoSearchRun()
#   # # tools_class = ResearchTools()
#   # tools = [search_tool]

#   # researcher = researcher(topic=topic, tools=tools)
#   # writer = writer(topic=topic, tools=tools)

#   # search_task = research_task(topic=topic, tools=tools, researcher=researcher)
#   # writing_task = write_task(topic=topic, tools=tools, writer=writer)
  
#   # crew = Crew(
#   #   agents=[researcher, writer],
#   #   tasks=[search_task, writing_task],
#   #   process=Process.sequential  # Optional: Sequential task execution is default
#   # )

#   # result = crew.kickoff()
#   # return result

app.include_router(prefix_router)