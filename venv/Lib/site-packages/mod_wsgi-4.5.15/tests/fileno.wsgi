import sys

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    output += "\nsys.stderr type:" + str(type(sys.stderr))

    if hasattr(sys.stderr, 'fileno'):
        if callable(sys.stderr.fileno):
            output += "\nabout to call fileno()"
            i = sys.stderr.fileno()

    response_headers = [('Content-type', 'text/plain'),
                    ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
