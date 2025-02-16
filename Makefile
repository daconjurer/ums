DIRS = ums/ tests/

.PHONY: lint format pyright test coverage

# Default to empty, can be overridden with make lint DIFF=1
DIFF_FLAG = $(if $(DIFF),--diff,)

lint:
	poetry run ruff check $(DIFF_FLAG) $(DIRS) && poetry run ruff check --select I $(DIFF_FLAG) $(DIRS)

format:
	poetry run ruff format $(DIFF_FLAG) $(DIRS)

typecheck:
	poetry run pyright $(DIRS)

test:
	poetry run coverage run -m pytest tests --full-trace

coverage:
	poetry run coverage report -m

coverage-html:
	poetry run coverage html

# Convenience target to run all checks
check: lint format typecheck test coverage coverage-html
