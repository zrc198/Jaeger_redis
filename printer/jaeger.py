from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import inject, extract
from opentelemetry.trace import Status, StatusCode


def init_otel_tracer(service_name="unnamed_service"):
    resource = Resource(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


def otel_tracer(tracer, span_name="unnamed_span"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = args[0]
            context = extract(data.get("jaeger_context", {}))

            with tracer.start_as_current_span(span_name, context=context) as span:
                service_name = trace.get_tracer_provider().resource.attributes.get(
                    "service.name"
                )
                span.set_attribute("peer.service", service_name)
                span.set_attribute("component", span_name)
                span.set_attribute("jaeger.trace_id", str(span.context.trace_id))
                span.set_attribute("payload", str(args[0]))
                for key, value in kwargs.items():
                    span.set_attribute(f"kwargs.{key}", str(value))
                jaeger_context = {}
                inject(jaeger_context)
                args[0]["jaeger_context"] = jaeger_context
                return func(*args, **kwargs)

        return wrapper

    return decorator


def mark_span_as_error(exc):
    current_span = trace.get_current_span()
    current_span.set_status(Status(StatusCode.ERROR, str(exc)))
    current_span.set_attribute("error", True)
    current_span.set_attribute("error.message", str(exc))
