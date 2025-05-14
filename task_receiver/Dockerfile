FROM python:3.13-alpine
WORKDIR /app
COPY task_receiver.py .
COPY jaeger.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "task_receiver.py"]
