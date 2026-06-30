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

.PHONY: check_release_env
check_release_env:
ifndef RELEASE
	$(error RELEASE is undefined. Please set it to either ["major", "minor", "patch"])
endif

.PHONY: bump_version
bump_version: check_release_env
	uvx bump2version $(RELEASE)
		$(eval NEW_VERSION := $(shell uvx bump2version \
	                            --allow-dirty \
	                            --dry-run \
	                            --list $(RELEASE) \
	                            | tail -1 \
	                            | sed s,"^.*=",,))
	git commit --amend --no-edit

.PHONY: gen_news
gen_news: check_release_env
	$(eval CURRENT_VERSION := $(shell uvx bump2version \
	                            --allow-dirty \
	                            --dry-run \
	                            --list $(RELEASE) \
	                            | grep current_version \
	                            | sed s,"^.*=",,))
	uvx towncrier build --version $(CURRENT_VERSION) --name pytest-pystack

.PHONY: release
release: check_release_env bump_version gen_news  ## Prepare release
