# Base Image
FROM python:3.11

# Set Directory
WORKDIR /usr/src/fireku

# Copy files
COPY . .

# Install requirements
RUN pip install -r requirements.txt

# Listen on port 5000
EXPOSE 5000

# Run the script
CMD ["python", "./main.py"]