FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY rai_system_prompt.py .
COPY tiered_recommendations.py .
COPY knowledge_loader.py .
COPY response_adapter.py .
COPY adaptive_prompt_builder.py .
COPY catalog_integration.py .
COPY dynamic_resources.py .

# Copy knowledge base files
COPY knowledge/ ./knowledge/

# Copy shared folder if exists
COPY shared/ ./shared/

# Create cache directory for dynamic resources
RUN mkdir -p ./cache

EXPOSE 8080

# Increase timeout to 120s for Azure OpenAI calls which can take 60-90s
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "--workers", "2", "app:app"]
