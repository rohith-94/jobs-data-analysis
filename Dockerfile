# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src, conf directories, and .env file into the container
COPY src/ ./src/
COPY conf/ ./conf/
COPY .env ./.env

# Command to run your application
CMD ["python", "src/main.py"]  # Replace with the actual entry point of your application
