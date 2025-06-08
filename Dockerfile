FROM python:3.10
WORKDIR /app
COPY bot/ /app/
COPY bot/requirements.txt /app/
COPY .env /app/
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "main.py"]

