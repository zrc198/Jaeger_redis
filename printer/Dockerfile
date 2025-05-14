FROM python:3.13-alpine
WORKDIR /app
COPY printer.py .
COPY jaeger.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "printer.py"]
