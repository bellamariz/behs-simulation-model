.PHONY: test run clean

test:
	PYTHONPATH=. pytest

run:
	python3 main.py

clean:
	rm -rf .pytest_cache */__pycache__