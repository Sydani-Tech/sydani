
from langchain_community.tools import DuckDuckGoSearchRun
from urllib.parse import urlparse
from langchain.tools import tool
from docx import Document
from pydantic import BaseModel, Field
import io
import PyPDF2
import requests


def get_file(file_url):
    # Parse the URL to get the filename
    parsed_url = urlparse(file_url)
    filename = parsed_url.path.split('/')[-1]

    # Download the file
    response = requests.get(file_url)
    file = io.BytesIO(response.content)
    # Check if the request was successful
    if response.status_code == 200:
        # Determine file type based on file extension
        file_extension = filename.split('.')[-1].lower()
        if file_extension == 'txt':
            return {'type': 'Text File'}
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            return {'type': 'Image File'} 
        elif file_extension in ['pdf']:
            return {'type': 'PDF File', 'content': file}
        elif file_extension in ['doc', 'docx']:
            return {'type': 'Word Document', 'content': file}
        else:
            return {'type': 'Unknown File Type'}
    else:
        return {'type': 'Failed to download file'}
    
def cv_loader(file_url):
    try:
        file = get_file(file_url=file_url)
        file_type = file['type']
        file_content = file['content']
        text = ""

        if file_type == 'PDF File':
            pdf_reader = PyPDF2.PdfReader(file_content)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            
        elif file_type == 'Word Document':  
            doc = Document(file_content)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        
        return text
    except:
        return None
    
# search tools
# class ResearchTools:
#     def __init__(self) -> None:
#       pass

#     def search_tool(self, query=""):
#         print('query: ', query)
#         st = DuckDuckGoSearchRun()
#         return st
    
# multi parm tool e.g

# from pydantic import BaseModel, Field

# class CalculationInput(BaseModel):
#     operation: str
#     factor: float

# @tool("perform_calculation", args_schema=CalculationInput, return_direct=True)
# def perform_calculation(operation: str, factor: float):
#     result = eval(operation) * factor