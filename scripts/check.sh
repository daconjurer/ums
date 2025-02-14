#! /bin/bash

echo "Running ruff checks..."
make lint
if [ $? -ne 0 ]; then
    echo "Error: ruff checks failed"
    exit 1
fi
echo "DONE!"

echo "Running ruff format..."
make format
if [ $? -ne 0 ]; then
    echo "Error: ruff format failed"
    exit 1
fi
echo "DONE!"

echo "Running type checks..."
make typecheck
if [ $? -ne 0 ]; then
    echo "Error: type checking failed"
    exit 1
fi
echo "DONE!"
