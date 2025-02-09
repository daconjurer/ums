DIRS = ums/ tests/

.PHONY: lint format pyright test coverage

lint:
	poetry run ruff check --fix $(DIRS) && poetry run ruff check --select I --fix $(DIRS)

format:
	poetry run ruff format $(DIRS)

pyright:
	poetry run pyright $(DIRS)

test:
	poetry run coverage run -m pytest tests --full-trace

coverage:
	poetry run coverage report -m

coverage-html:
	poetry run coverage html

# Convenience target to run all checks
check: lint format pyright test coverage coverage-html
