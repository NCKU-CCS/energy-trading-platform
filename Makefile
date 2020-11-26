PKG=pt

.PHONY: all clean version init flake8 pylint lint test coverage

init: clean
	pipenv --python 3.6
	pipenv install
	# pipenv install --dev


dev: init
	pipenv install --dev
	pipenv run pre-commit install -t commit-msg

commit:
	pipenv run cz commit

flake8:
	pipenv run flake8

pylint:
	pipenv run pylint $(PKG) --ignore=tests

black:
	pipenv run black $(PKG) --skip-string-normalization

lint: flake8 pylint

build:
	docker build -t et_platform pt --no-cache

run:
	pipenv run python pt/app.py

clean:
	find . -type d -name '__pycache__' -delete
