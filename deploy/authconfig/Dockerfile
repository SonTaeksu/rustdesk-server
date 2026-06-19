FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
# 운영: gunicorn (워커 2). 환경변수 AAD_TENANT/AAD_CLIENT/RUSTDESK_KEY 필요.
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "2", "app:app"]
