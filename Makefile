install:
	pip install -e .

setup:
	python start.py

run:
	uvicorn api.main:app --reload --port 8000

demo:
	streamlit run demo/streamlit_app.py

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	black .

generate:
	fast-readme .
