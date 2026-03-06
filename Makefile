install:
	pip install -r requirements.txt

run:
	uvicorn backend.main:app --reload --port 8000

demo:
	streamlit run demo/streamlit_app.py

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	black .
