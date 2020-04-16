
PYTHON=python
VERSION=`cut -d "'" -f 2 alertaclient/version.py`

all:	help

help:
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "Commands:"
	@echo "   init    Initialise environment"
	@echo "   dev     Initialise dev environment"
	@echo "   pylint  Lint source code"
	@echo "   mypy    Type checking"
	@echo "   hooks   Run pre-commit hooks"
	@echo "   clean   Clean source"
	@echo "   test    Run tests"
	@echo "   run     Run application"
	@echo "   tag     Git tag with current version"
	@echo "   upload  Upload package to PyPI"
	@echo ""

init:
	pip install -r requirements.txt --upgrade
	pip install -e .

dev:
	pip install -r requirements-dev.txt --upgrade
	pre-commit install
	pre-commit autoupdate

pylint:
	@pip -q install pylint
	pylint --rcfile pylintrc alertaclient

mypy:
	@pip -q install mypy==0.620
	mypy alertaclient/

hooks:
	pre-commit run --all-files

clean:
	find . -name "*.pyc" -exec rm {} \;
	rm -Rf build dist *.egg-info

test:
	pytest

test.integration:
	docker-compose -f docker-compose.ci.yaml build sut
	docker-compose -f docker-compose.ci.yaml up --exit-code-from sut
	docker-compose -f docker-compose.ci.yaml rm --stop --force

run:
	alerta top

tag:
	git tag -a v$(VERSION) -m v$(VERSION)
	git push --tags

upload:
	$(PYTHON) setup.py sdist bdist_wheel
	twine upload dist/*
