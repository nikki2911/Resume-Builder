# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app code into the container
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Command to run the Streamlit application
# --server.port=8501: Ensures Streamlit listens on this port
# --server.address=0.0.0.0: Allows access from any IP address
# --server.enableCORS=false: Disable CORS for simpler deployment (adjust as needed for production)
# --server.headless=true: Run Streamlit in headless mode
ENTRYPOINT ["streamlit", "run", "ATSExpert_AI.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.headless=true"]