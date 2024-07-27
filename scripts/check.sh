#! /bin/bash

echo "ruff check --diff ums/"
ruff check --select I --diff ums/ tests/ db/
if [ $? -ne 0 ]; then
    echo "Error: ruff check failed"
    exit 1
fi
echo "DONE!"

echo "ruff format --diff ums/"
ruff format --diff ums/ tests/ db/
if [ $? -ne 0 ]; then
    echo "Error: ruff format failed"
    exit 1
fi
echo "DONE!"

echo "mypy ums/"
mypy ums/
if [ $? -ne 0 ]; then
    echo "Error: mypy failed"
    exit 1
fi
echo "DONE!"
