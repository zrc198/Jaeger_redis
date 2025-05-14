import redis
import json
from jaeger import init_otel_tracer, otel_tracer

r = redis.Redis(host="redis", port=6379, decode_responses=True)
tracer = init_otel_tracer(service_name="printer")


@otel_tracer(tracer, span_name="print_task_result")
def print_task_result(task):
    print(f"Result: {task['result']}")


if __name__ == "__main__":
    print("printer started")
    while True:
        task_json = r.blpop("results")[1]
        task = json.loads(task_json)
        print_task_result(task)
