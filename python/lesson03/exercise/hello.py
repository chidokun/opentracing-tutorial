import requests
import sys
import time
from lib.tracing import init_tracer
from opentracing_instrumentation.request_context import get_current_span, span_in_context


def say_hello(hello_to):
    with tracer.start_span('say-hello') as span:
        span.set_tag('hello-to', hello_to)
        with span_in_context(span):
            hello_str = format_string(hello_to)
            print_hello(hello_str)

def format_string(hello_to):
    with tracer.start_span('format', child_of=get_current_span()) as span:
        hello_str = http_get(8081, 'format', 'helloTo', hello_to)
        span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str

def print_hello(hello_str):
    with tracer.start_span('println', child_of=get_current_span()) as span:
        http_get(8082, 'publish', 'helloStr', hello_str)
        span.log_kv({'event': 'println'})

def http_get(port, path, param, value):
    url = 'http://localhost:%s/%s' % (port, path)
    r = requests.get(url, params={param: value})
    assert r.status_code == 200
    return r.text
        

# main
assert len(sys.argv) == 2

tracer = init_tracer('hello-world')

hello_to = sys.argv[1]
say_hello(hello_to)

# yield to IOLoop to flush the spans
time.sleep(2)
tracer.close()
