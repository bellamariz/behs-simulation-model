.PHONY: test run clean

lint:
	pylint $(shell git ls-files '*.py') --disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,consider-using-min-builtin,too-few-public-methods,line-too-long

test:
	PYTHONPATH=. pytest

install:
	pip3 install -r requirements.txt

run:
	python3 main.py

clean:
	rm -rf .pytest_cache */__pycache__ */*/__pycache__