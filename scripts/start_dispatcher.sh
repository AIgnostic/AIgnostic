#!/bin/bash
# Start the dispatcher in the background
poetry run python -u -m dispatcher &

# Start the API server
poetry run uvicorn main:app --host 0.0.0.0 --reload
