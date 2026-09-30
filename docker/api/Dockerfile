FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 libgomp1 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml requirements.txt ./
COPY kdp_factory ./kdp_factory
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["uvicorn","kdp_factory.api:app","--host","0.0.0.0","--port","8000"]
