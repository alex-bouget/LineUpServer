FROM python:3.11-alpine3.21

RUN apk add --no-cache \
    gcc musl-dev linux-headers python3-dev

    # Make port 80 available to the world outside this container
EXPOSE 80

# Set the working directory
WORKDIR /runtime

ENTRYPOINT ["/entrypoint.sh"]

ENV LUP_SERVER_DOCKER=1

# Copy the current directory contents into the container at /app
COPY ./src /runtime

COPY ./entrypoint.sh /entrypoint.sh

COPY ./requirements.txt /runtime/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /runtime/requirements.txt && \
    chmod +x /entrypoint.sh
