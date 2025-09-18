# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the API key (will be passed in at runtime)
ENV GOOGLE_API_KEY=""

# Run the app when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "600", "app:app"]