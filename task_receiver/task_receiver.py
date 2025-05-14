import redis
import json
from jaeger import init_otel_tracer, otel_tracer

r = redis.Redis(host="redis", port=6379, decode_responses=True)
tracer = init_otel_tracer(service_name="task_receiver")


@otel_tracer(tracer, span_name="send_task")
def send_task(data):
    task = json.dumps(data)
    r.rpush("tasks", task)
    print(f"Sent task: {a} / {b}")


if __name__ == "__main__":
    print("task_receiver started")
    while True:
        try:
            a = int(input("Enter first number: "))
            b = int(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter integers.")
            continue
        data = {"a": a, "b": b}
        send_task(data)
