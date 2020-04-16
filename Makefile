
PYTHON=python
VERSION=`cut -d "'" -f 2 alertaclient/version.py`
.DEFAULT_GOAL:=help

all:	help

## init			- Initialise environment.
init:
	pip install -r requirements.txt --upgrade
	pip install -e .

## dev			- Initialise dev environment.
dev:
	pip install -r requirements-dev.txt --upgrade
	pre-commit install
	pre-commit autoupdate

## hooks			- Run pre-commit hooks.
hooks:
	pre-commit run --all-files

## lint			- Lint and type checking.
lint:
	@pip -q install pylint
	pylint --rcfile pylintrc alertaclient
	@pip -q install mypy==0.620
	mypy alertaclient/

## clean			- Clean source.
clean:
	find . -name "*.pyc" -exec rm {} \;
	rm -Rf build dist *.egg-info

## test.unit		- Run unit tests.
test.unit:
	pip install coveralls
	pytest --cov=alertaclient tests/unit

## test.integration	- Run integration tests.
test.integration:
	docker-compose -f docker-compose.ci.yaml build sut
	docker-compose -f docker-compose.ci.yaml up --exit-code-from sut
	docker-compose -f docker-compose.ci.yaml rm --stop --force

## run			- Run application.
run:
	alerta top

## tag			- Git tag with current version.
tag:
	git tag -a v$(VERSION) -m v$(VERSION)
	git push --tags

## upload			- Upload package to PyPI.
upload:
	$(PYTHON) setup.py sdist bdist_wheel
	twine upload dist/*

## help			- Show this help.
help: Makefile
	@sed -n 's/^##//p' $<
