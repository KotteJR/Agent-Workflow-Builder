*-* Exposing APIs & models *-*

export LLM_PROVIDER=openai
export OPENAI_API_KEY=YOURKEY
export SMALL_MODEL=gpt-4.1-mini
export LARGE_MODEL=gpt-4.1
export EMBEDDING_MODEL=text-embedding-3-small

export IMAGE_PROVIDER=gemini
export GOOGLE_API_KEY=your-google-api-key


*-* Setting up requirements and FastAPI *-* 

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000


*-* nGrok Start *-* 
./start-backend-ngrok.sh


*-* Local Frontend *-*
npm run dev