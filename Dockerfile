# Use a lightweight Python base image
FROM python:3.11-slim

# Install uv to speed up dependency installation
RUN pip install uv

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency list
COPY requirements.txt .

# Install dependencies into the system python
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the rest of your application code
COPY . .

# --- HUGGING FACE SPECIFIC CONFIGURATION ---
# Create a non-root user (Required by Hugging Face security)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Hugging Face Spaces always listen on port 7860
ENV PORT=7860

# Command to run the app
CMD ["python", "main.py"]
