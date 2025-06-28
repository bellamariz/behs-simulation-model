.PHONY: test run clean

lint:
	pylint $(shell git ls-files '*.py') --disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,consider-using-min-builtin,too-few-public-methods,line-too-long,duplicate-code,useless-parent-delegation

test:
	PYTHONPATH=. pytest

install:
	pip3 install -r requirements.txt

run:
	python3 main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache