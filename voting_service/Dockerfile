FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5002
CMD ["gunicorn", "-b", "0.0.0.0:5002", "app:app"]
