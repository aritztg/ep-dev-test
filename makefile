run:
	python app/simple-api.py

tests:
	python -m unittest discover app

lint:
	ruff check app
	isort app --check-only
	pylint app