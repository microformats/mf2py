install:
	poetry install
tests:
	poetry run pytest -s -vv --doctest-modules --doctest-glob README*
lint:
	poetry run black .
	poetry run isort .
docs_dev:
	poetry run mkdocs serve
docs_deploy:
	poetry run mkdocs gh-deploy
publish:
	poetry publish --build
