# ai-study-qg
AI-powered study question generator using Qwen 3 via OpenRouter

open .evn and paste your openrouter key, inigration with openrouter only.
backend/qg has the name of the model you're using, Qwen3 235B A22B Instruct 2507 is the default, works the best, is the fastest (with cerebras as provider) and good at learning with datasets and absorbing knowlege from them.

can be run locally. 

steps:
 open windows terminal in adminitrator mode
 locate path to ai-study-qg
 type venv/scripts/activate (amke sure you hace executing scripts on)
 then  uvicorn backend.app.main:app --reload --port 8000
 KEEP THIS OPEN. THIS IS OUR API.
 in another terminal tap, do the same until after executing venv/scripts/activate
 type  streamlit run frontend/app.py  and enter
 this is the local host website, this is the "app"

 KEEP BOTH TERMINAL TABS OPEN.

 DEBUGGING

 http://127.0.0.1:8000/ (should always not tell you any info at all (on purpose) if this displays actually useful information, something is wrong)
 http://127.0.0.1:8000/docs (tells you which services are online and running, should usally be /ingest and /generate, if anything else is there under the default tab, notify me.)

 thats it.

1. Prerequisites

Make sure the machine has:

Python 3.10+

SQLite (comes with Python, so no extra install usually)

Git (for cloning / version control)