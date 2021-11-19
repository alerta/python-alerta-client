#!make

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip --disable-pip-version-check
PYLINT=$(VENV)/bin/pylint
MYPY=$(VENV)/bin/mypy
BLACK=$(VENV)/bin/black
TOX=$(VENV)/bin/tox
PYTEST=$(VENV)/bin/pytest
PRE_COMMIT=$(VENV)/bin/pre-commit
WHEEL=$(VENV)/bin/wheel
TWINE=$(VENV)/bin/twine
GIT=git

.DEFAULT_GOAL:=help

-include .env .env.local .env.*.local

ifndef PROJECT
$(error PROJECT is not set)
endif

VERSION=$(shell cut -d "'" -f 2 $(PROJECT)/version.py)

PKG_SDIST=dist/*-$(VERSION).tar.gz
PKG_WHEEL=dist/*-$(VERSION)-*.whl

all:	help

$(PIP):
	python3 -m venv $(VENV)

$(PYLINT): $(PIP)
	$(PIP) install pylint==2.11.1

$(MYPY): $(PIP)
	$(PIP) install mypy==0.812

$(BLACK): $(PIP)
	$(PIP) install black==21.11b1

$(TOX): $(PIP)
	$(PIP) install tox

$(PYTEST): $(PIP)
	$(PIP) install pytest==6.2.5 pytest-cov==3.0.0

$(PRE_COMMIT): $(PIP)
	$(PIP) install pre-commit==2.15.0

$(WHEEL): $(PIP)
	$(PIP) install wheel

$(TWINE): $(PIP)
	$(PIP) install wheel twine

ifdef TOXENV
toxparams?=-e $(TOXENV)
endif

## install			- Install dependencies.
install: $(PIP)
	$(PIP) install -r requirements.txt

## format			- Code formatter.
format: $(BLACK)
	$(BLACK) -l120 -S -v $(PROJECT)

## lint			- Lint and type checking.
lint: $(PYLINT) $(MYPY) $(BLACK)
	$(PYLINT) --rcfile pylintrc $(PROJECT)
	$(MYPY) $(PROJECT)/
	$(BLACK) -l120 -S --check -v $(PROJECT) || true

## hooks			- Run pre-commit hooks.
hooks: $(PRE_COMMIT)
	$(PRE_COMMIT) run -a

## test			- Run all tests.
test: test.unit test.integration

## test.unit		- Run unit tests.
test.unit: $(TOX) $(PYTEST)
	$(TOX) $(toxparams)

## test.integration	- Run integration tests.
test.integration:
	docker-compose -f docker-compose.ci.yaml rm --stop --force
	docker-compose -f docker-compose.ci.yaml pull
	docker-compose -f docker-compose.ci.yaml build sut
	docker-compose -f docker-compose.ci.yaml up --exit-code-from sut
	docker-compose -f docker-compose.ci.yaml rm --stop --force

## run			- Run application.
run:
	alerta

## tag			- Git tag with current version.
tag:
	$(GIT) tag -a v$(VERSION) -m "version $(VERSION)"
	$(GIT) push --tags

## build			- Build package.
build: $(PIP) $(WHEEL) $(PKG_SDIST) $(PKG_WHEEL)

$(PKG_SDIST):
	$(PYTHON) setup.py sdist
$(PKG_WHEEL):
	$(PYTHON) setup.py bdist_wheel

## upload			- Upload package to PyPI.
upload: $(TWINE)
	$(TWINE) upload dist/*

## clean			- Clean source.
clean:
	rm -rf $(VENV)
	rm -rf .tox
	rm -rf dist
	rm -rf build
	find . -name "*.pyc" -exec rm {} \;

## help			- Show this help.
help: Makefile
	@echo ''
	@echo 'Usage:'
	@echo '  make [TARGET]'
	@echo ''
	@echo 'Targets:'
	@sed -n 's/^##//p' $<
	@echo ''

	@echo 'Add project-specific env variables to .env file:'
	@echo 'PROJECT=$(PROJECT)'

.PHONY: help lint test build sdist wheel clean all
