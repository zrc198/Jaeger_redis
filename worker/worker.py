import redis
import json
from jaeger import init_otel_tracer, otel_tracer, mark_span_as_error


r = redis.Redis(host="redis", port=6379, decode_responses=True)
tracer = init_otel_tracer(service_name="worker")


@otel_tracer(tracer, span_name="process_task")
def process_task(task):
    a = task["a"]
    b = task["b"]
    try:
        result = a / b
    except ZeroDivisionError as exc:
        result = "Error: Division by zero"
        mark_span_as_error(exc)
    task["result"] = result
    updated_task = json.dumps(task)
    print(f"Processed task: {a} / {b} = {result}")
    r.rpush("results", updated_task)


if __name__ == "__main__":
    print("worker started")
    while True:
        task_json = r.blpop("tasks")[1]
        task = json.loads(task_json)
        process_task(task)
