.PHONY: test run clean

lint:
	pylint $(shell git ls-files '*.py') --disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,consider-using-min-builtin

test:
	PYTHONPATH=. pytest

run:
	python3 main.py

clean:
	rm -rf .pytest_cache */__pycache__