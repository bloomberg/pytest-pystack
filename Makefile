PYTHON ?= python

SRCDIR := src
python_files := $(shell find * -name \*.py -not -path '*/\.*')

.PHONY: check
check:
	$(PYTHON) -m pytest -vv tests/

.PHONY: format
format:
	$(PYTHON) -m isort $(python_files)
	$(PYTHON) -m black $(python_files)

.PHONY: lint
lint:
	$(PYTHON) -m ruff check $(python_files)
	$(PYTHON) -m isort --check $(python_files)
	$(PYTHON) -m black --check $(python_files)
