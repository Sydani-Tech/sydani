# Application Tracking System Using Langchain and CrewAi

## Setup

Clone the repo and cd into the project folder - make sure your python version is >= 3.10

### Follow the instruction

1. Create python virtual environment `python -m venv .venv` and activate it using `.venv/Scripts/Activate`

2. Install the dependencies run: `pip install -r requirements.txt`

3. Rename `.env-example` file to `.env` and edit the file to add your `OPENAI_API_KEY` put any string on `GOOGLE_API_KEY` if you are not testing with google gemini

4. Run: `uvicorn main:app --reload` this will run the app on localhost port 8000

5. Use Postman or any other API testing platform send a post request with raw data to
  url: `http://127.0.0.1:8000/screen` raw-data: `{"cv_url": "CV URL From ERP", "criteria": "Job requirement from ERP"}`
  