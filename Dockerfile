FROM python:3.11-alpine3.21

RUN apk add --no-cache \
    gcc musl-dev linux-headers python3-dev

    # Make port 80 available to the world outside this container
EXPOSE 80

# Set the working directory
WORKDIR /app/src

ENTRYPOINT ["/app/entrypoint.sh"]

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    chmod +x /app/entrypoint.sh
