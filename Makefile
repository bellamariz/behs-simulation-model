.PHONY: lint test install run clean

lint:
	PYTHONPATH=. pylint $(shell git ls-files 'src/*.py') --disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,consider-using-min-builtin,too-few-public-methods,line-too-long,duplicate-code,useless-parent-delegation,consider-using-from-import

test:
	PYTHONPATH=. pytest

install:
	pip3 install -r requirements.txt

run:
	PYTHONPATH=. python3 main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache

help:
	@echo "Available targets:"
	@echo " > lint    - Run code linter using pylint"
	@echo " > test    - Run unit tests using pytest"
	@echo " > install - Install project dependencies"
	@echo " > run     - Run the application"
	@echo " > clean   - Clean local pycache and pytest cache files"