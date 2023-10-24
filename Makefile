install:
	poetry install
tests:
	poetry run pytest --doctest-modules -s -vv --doctest-glob README*
publish:
	poetry publish --build
lint:
	poetry run black .
	poetry run isort .
