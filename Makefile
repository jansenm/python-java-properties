# Makefile

NAME=env

PYTHON := $(PWD)/env/bin/python
PYTHON_UNITTEST := $(PYTHON) -m unittest
PYTHON_JUNIT := $(PYTHON) -m xmlrunner
PYTHON_PIP := $(PYTHON) -m pip

test: build
	$(PYTHON_UNITTEST) discover

test-junit: build
	mkdir -p build/test/junit
	cd build/test/junit; $(PYTHON_JUNIT) discover -t ../../.. ../../../mjbiz

develop:
	$(PYTHON) setup.py develop

veryclean:
	rm -rf build/

clean: clean-doc clean-egg setup-clean
	find mjbiz -name __pycache__ | xargs rm -fr

check: setup-check

clean-doc:
	rm -rf doc/build/

clean-egg:
	rm -rf *.egg-info

.PHONY: doc
doc:
	cd doc && make html

setup-%:
	@echo "> python setup.py $*"
	$(PYTHON) setup.py $*

build: $(NAME) setup-build

$(NAME):
	@echo "* Creating virtual environment "
	pyvenv $(NAME)
	$(PYTHON_PIP) install -r requirements.txt

ez_setup.py:
	@echo "  - Installing setuptools"
	wget https://bootstrap.pypa.io/ez_setup.py -O - | $(NAME)/bin/python

