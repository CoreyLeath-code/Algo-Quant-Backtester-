.PHONY: install lint test demo benchmark build reproduce

install:
	python -m pip install -e ".[dev]"

lint:
	python -m compileall -q algoquant tests
	ruff check algoquant tests

test:
	python -m pytest tests -v --cov=algoquant --cov-config=.coveragerc --cov-report=term-missing --cov-report=xml --junitxml=pytest-results.xml

demo:
	python -m algoquant.cli --rows 1000 --seed 20260828

benchmark:
	python -m algoquant.benchmark --rows 5000 --iterations 50 --warmups 5 --seed 20260828 --output benchmark-results.json

build:
	python -m build

reproduce: lint test benchmark build
