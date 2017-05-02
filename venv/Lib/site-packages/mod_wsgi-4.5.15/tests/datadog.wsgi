from __future__ import print_function

import mod_wsgi
import traceback
import time
import os

from datadog import initialize

options = {
    'api_key':'8eacdd87e64131f47c69221d04526cfe',
    'app_key':'eefd4c940e22cd245d86474e7d3586f49bd9c2b5'
}

initialize(**options)

from datadog import statsd

try:
    mod_wsgi.request_data()
except RuntimeError:
    print('INACTIVE')

def wrapper(application):
    def _application(environ, start_response):
        print('WRAPPER', application)
        return application(environ, start_response)
    return _application

def event_handler(name, **kwargs):
    print('EVENT', name, kwargs, os.getpid(), mod_wsgi.application_group)
    if name == 'request_started':
        request = mod_wsgi.request_data()
        print('REQUEST', request)
        environ = kwargs['request_environ']
        start_time = time.time()
        request['start_time'] = start_time
        return dict(application=wrapper(kwargs['application']))
    elif name == 'request_finished':
        statsd.increment('mod_wsgi.request.count')
        statsd.histogram('mod_wsgi.request.response_time', kwargs.get('response_time'))
        statsd.gauge('mod_wsgi.request.cpu_user_time', kwargs.get('cpu_user_time'))
        statsd.gauge('mod_wsgi.request.cpu_system_time', kwargs.get('cpu_system_time'))
        statsd.gauge('mod_wsgi.request.output_length', kwargs.get('output_length'))
        request = mod_wsgi.request_data()
        print('REQUEST', request)
        print('FINISH', time.time()-request['start_time'])
        print('PROCESS', mod_wsgi.process_metrics()) 
    elif name == 'request_exception':
        exc_info = kwargs['exc_info']
        traceback.print_exception(*exc_info)

print('EVENTS', mod_wsgi.event_callbacks)

mod_wsgi.subscribe_events(event_handler)

print('CALLBACKS', mod_wsgi.event_callbacks)

def application(environ, start_response):
    failure_mode = environ.get('HTTP_X_FAILURE_MODE', '')

    failure_mode = failure_mode.split()

    if 'application' in failure_mode:
        raise RuntimeError('application')

    status = '200 OK'
    output = b'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    for i in range(100000):
      i**2

    try:
        yield output

        if 'yield' in failure_mode:
            raise RuntimeError('yield')
    finally:
        if 'close' in failure_mode:
            raise RuntimeError('close')
