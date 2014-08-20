NAME=env


test: build
	python -m unittest

develop:
	$(NAME)/bin/python setup.py develop

veryclean:
	rm -rf build/

clean: clean-doc clean-egg setup-clean
	find mjbiz -name __pycache__ | xargs rm -fr

clean-doc:
	rm -rf doc/build/

clean-egg:
	rm -rf *.egg-info

.PHONY: doc
doc:
	cd doc && make html

setup-%:
	@echo "> python setup.py $*"
	python setup.py $*

build: setup-build

setup: ez_setup.py $(NAME)
	@echo "  - Installing setuptools"
	wget https://bootstrap.pypa.io/ez_setup.py -O - | $(NAME)/bin/python
	@echo "  - Installing pip"
	$(NAME)/bin/easy_install pip

$(NAME):
	@echo "* Creating virtual environment "
	pyvenv $(NAME)

ez_setup.py:
	wget https://bootstrap.pypa.io/ez_setup.py

