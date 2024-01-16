FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY websocket_server /app/websocket_server

CMD ["python3", "websocket_server/server.py"]


