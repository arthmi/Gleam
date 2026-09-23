# Makefile
install:
	.venv/bin/pip install -r requirements.txt

dev:
	uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

start:
	uvicorn server.main:app --host 0.0.0.0 --port 8000

freeze:
	.venv/bin/pip freeze > requirements.txt

# lint:
# 	ruff check

# format:
# 	ruff format

# test:
# 	pytest

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
