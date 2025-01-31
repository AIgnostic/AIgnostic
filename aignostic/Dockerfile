# First stage: build
FROM python:3.12 AS builder

# Set the working directory in the container
WORKDIR /app

# Metadata
LABEL org.opencontainers.image.source="https://github.com/AIgnostic/AIgnostic"

# Install Node and pipx & poetry
RUN apt-get update && apt-get install -y --no-install-suggests --no-install-recommends curl
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y --no-install-suggests --no-install-recommends nodejs pipx
RUN pipx ensurepath
ENV PATH="/root/.local/bin:${PATH}"

RUN pipx install poetry

# Copy the application monorepo to the container
COPY ./package.json /app
COPY ./nx.json /app
COPY ./package-lock.json /app
COPY ./aignostic /app/aignostic

# Run npm ci
RUN npm ci

# Run poetry install via nx
RUN npx nx install aignostic --args="--only main"

# Copy venv & application code to new image
# Second stage: runtime
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/aignostic /app

# Create a non-root user and switch to it
RUN useradd -m appuser

# Change ownership
RUN chown -R appuser /app

# Switch
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI server
CMD ["./.venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
