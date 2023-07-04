install:
	poetry install
test:
	poetry run pytest
publish:
	poetry publish --build
lint:
	poetry run black .
	poetry run isort .
