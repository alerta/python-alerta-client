
PYTHON=python
VERSION=`cut -d "'" -f 2 alertaclient/version.py`

all:	help

help:
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "Commands:"
	@echo "   init    Initialise environment"
	@echo "   pylint  Lint source code"
	@echo "   clean   Clean source"
	@echo "   test    Run tests"
	@echo "   run     Run application"
	@echo "   tag     Git tag with current version"
	@echo "   upload  Upload package to PyPI"
	@echo ""

init:
	pip install -r requirements.txt

pylint:
	@pip -q install pylint
	pylint --rcfile pylintrc alertaclient

clean:
	find . -name "*.pyc" -exec rm {} \;
	rm -Rf build dist *.egg-info

test:
	nosetests tests

run:
	alerta top

tag:
	git tag -a v$(VERSION) -m v$(VERSION)

upload:
	$(PYTHON) setup.py sdist bdist_wheel upload

