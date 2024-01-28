#! /bin/bash
echo "ruff check --diff ums/"
ruff check --diff ums/
echo "DONE!"
echo "ruff format --diff ums/"
ruff format --diff ums/
echo "DONE!"
echo "mypy ums/"
mypy ums/
echo "DONE!"
