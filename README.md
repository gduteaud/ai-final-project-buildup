# Usage

## With Docker (recommended)
0. Install [Docker Desktop](https://www.docker.com/)

1. Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_openrouter_api_key
# Optional (defaults if not set)
LLM_MODEL=mistralai/mistral-7b-instruct:free
```

2. Build and run with Docker Compose:

```
docker compose up --build -d
```

3. Open your app(s):
   - App 1 (folder `1/`): http://localhost:8501
   - App 2 (folder `2/`): http://localhost:8502
   - App 3 (folder `3/`): http://localhost:8503
   - App 4 (folder `4/`): http://localhost:8504

To stop:

```
docker compose down
```

Run a single app with plain Docker

```
# Build any app by passing APP_DIR build-arg (1, 2, 3, or 4)
docker build --build-arg APP_DIR=1 -t app1 .
docker run --rm -p 8501:8501 --env-file .env app1
```

## Locally

1. Download or clone the repo
2. Create a virtual environment (`python -m venv my-env`)
3. Activate your newly created virtual environment (`my-env\Scripts\activate` or equivalent)
4. Install the dependencies (`pip install -r requirements.txt`)
5. `cd` into one of the numbered subdirectories (1/2/3/4)
6. Run `streamlit run app.py`