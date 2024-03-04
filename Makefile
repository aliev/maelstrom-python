include .env
.PHONY: clean clean-pyc clean-build help
.DEFAULT_GOAL := help

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

fix: ## fix black / isort
	pre-commit run --all-files

install: clean ## install the package to the active Python's site-packages
	python setup.py install

dev-install: clean ## install the package and test dependencies for local development
	python -m pip install --upgrade pip
	pip install -e ."[dev]"
	pre-commit install

test-echo:
	${MAELSTROM_BIN_PATH}/maelstrom test -w echo --bin $(shell which mnode) --time-limit 5 --log-stderr

test-broadcast:
	${MAELSTROM_BIN_PATH}/maelstrom test -w broadcast --bin $(shell which mnode) --time-limit 20 --rate 100 --node-count 25 --topology grid --latency 100

test-performance:
	${MAELSTROM_BIN_PATH}/maelstrom test -w broadcast --bin $(shell which mnode) --time-limit 20 --topology tree4 --nemesis partition
