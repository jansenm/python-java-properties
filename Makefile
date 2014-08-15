NAME=env

.PHONY: doc
doc:
	cd doc && make html

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

