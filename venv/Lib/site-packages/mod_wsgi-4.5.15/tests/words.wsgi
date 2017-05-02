import os

def application(environ, start_response):
    status = '200 OK'

    #name = '/usr/share/dict/words'
    name = '/tmp/file.txt'
    size = os.stat(name).st_size

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(size))]
    start_response(status, response_headers)

    return environ['wsgi.file_wrapper'](open(name))
