FROM python:3.13-alpine3.21

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]