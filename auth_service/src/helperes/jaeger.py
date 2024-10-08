# from opentelemetry import trace
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
#
#
# def configure_tracer(jaeger_host: str, jaeger_port: int, service_name: str) -> None:
#     resource = Resource(attributes={SERVICE_NAME: service_name})
#     trace.set_tracer_provider(TracerProvider(resource=resource))
#     trace.get_tracer_provider().add_span_processor(
#         BatchSpanProcessor(
#             JaegerExporter(
#                 agent_host_name=jaeger_host,
#                 agent_port=jaeger_port,
#             )
#         )
#     )
#     # Чтобы видеть трейсы в консоли
#     trace.get_tracer_provider().add_span_processor(
#         BatchSpanProcessor(ConsoleSpanExporter())
#     )
