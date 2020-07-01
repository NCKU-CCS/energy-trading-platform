PKG=pt

.PHONY: all clean version init flake8 pylint lint test coverage

init: clean
	pipenv --python 3.6
	pipenv install
	# pipenv install --dev


dev: init
	pipenv install --dev
	pipenv run pre-commit install
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

build_docker:
	pipenv lock --requirements > platform/requirements.txt
	docker login
	docker build --no-cache -t platform_docker:latest platform/
	docker tag platform_docker ttw225/platform_docker
	docker push ttw225/platform_docker

clean:
	find . -type d -name '__pycache__' -delete
