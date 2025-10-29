FROM python:2.7

WORKDIR /app

# Copy the application files
COPY techtrends/ .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Initialize the database
RUN python init_db.py

# Make port 3111 available to the world outside this container
EXPOSE 3111

# Define environment variable for Flask to run in production mode
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["python", "app.py"]