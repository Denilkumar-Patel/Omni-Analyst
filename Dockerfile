# Use a lightweight, official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /project

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (no-cache keeps the image size small)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit uses
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]