# 1. Use an official Python image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy our project files into the container
COPY . .

# 4. Run the script when the container starts
CMD ["python", "scripts/process_sales.py"]