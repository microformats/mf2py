install:
	poetry install
tests:
	poetry run pytest -s -vv --doctest-modules --doctest-glob README*
publish:
	poetry publish --build
lint:
	poetry run black .
	poetry run isort .
