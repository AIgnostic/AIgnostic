FROM node:20

# Set the working directory in the container
WORKDIR /app

# Copy the application monorepo to the container
COPY ./package.json /app
COPY ./nx.json /app
COPY ./package-lock.json /app

RUN npm ci

COPY ./frontend /app/frontend



# # Create a non-root user and switch to it
# RUN useradd -m appuser

# # Change ownership
# RUN chown -R appuser /app

# # Switch
# USER appuser
