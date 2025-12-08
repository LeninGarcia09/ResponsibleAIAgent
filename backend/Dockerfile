FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY rai_system_prompt.py .
COPY knowledge_loader.py .

# Copy knowledge base files
COPY knowledge/ ./knowledge/

# Copy shared folder if exists
COPY shared/ ./shared/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
