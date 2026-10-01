FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY server.py /app/server.py
EXPOSE 8189
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8189"]
