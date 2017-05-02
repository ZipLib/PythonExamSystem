from __future__ import print_function

import mod_wsgi
import traceback
import time
import os
import threading

from influxdb import InfluxDBClient

#database_host = 'dshome.local'
database_host = '192.168.99.100'
database_port = 8086
database_user = 'root'
database_pass = 'root'
database_name = 'metrics'

influxdb_client_1 = InfluxDBClient(database_host, database_port,
        database_user, database_pass, database_name)

influxdb_client_2 = InfluxDBClient(database_host, database_port,
        database_user, database_pass, database_name)

last_metrics = None

def monitor(*args):
    global last_metrics

    while True:
        current_metrics = mod_wsgi.process_metrics()

        if last_metrics is not None:
            cpu_user_time = (current_metrics['cpu_user_time'] -
                    last_metrics['cpu_user_time'])
            cpu_system_time = (current_metrics['cpu_system_time'] -
                    last_metrics['cpu_system_time'])

            request_busy_time = (current_metrics['request_busy_time'] -
                    last_metrics['request_busy_time'])

            request_threads = current_metrics['request_threads']

            # report data

            timestamp = int(current_metrics['current_time'] * 1000000000)

            samples = []

            item = {}
            item['time'] = timestamp
            item['measurement'] = 'process'

            fields = {}

            fields['cpu_user_time'] = cpu_user_time
            fields['cpu_system_time'] = cpu_system_time

            fields['request_busy_time'] = request_busy_time
            fields['request_busy_usage'] = (request_busy_time /
                    mod_wsgi.threads_per_process)

            fields['threads_per_process'] = mod_wsgi.threads_per_process
            fields['request_threads'] = request_threads

            item['fields'] = fields
            samples.append(item)

            influxdb_client_2.write_points(samples)

        last_metrics = current_metrics

        current_time = current_metrics['current_time']
        delay = max(0, (current_time + 1.0) - time.time())
        time.sleep(delay)

thread = threading.Thread(target=monitor)
thread.setDaemon(True)
thread.start()

try:
    mod_wsgi.request_data()
except RuntimeError:
    print('INACTIVE')

def wrapper(application):
    def _application(environ, start_response):
        #print('WRAPPER', application)
        return application(environ, start_response)
    return _application

def event_handler(name, **kwargs):
    #print('EVENT', name, kwargs, os.getpid(), mod_wsgi.application_group)
    if name == 'request_started':
        request = mod_wsgi.request_data()
        #print('REQUEST', request)
        environ = kwargs['request_environ']

        #start_time = time.time()
        #request['start_time'] = start_time
        #return dict(application=wrapper(kwargs['application_object']))

        request['request_start'] = kwargs['request_start']
        request['queue_start'] = kwargs['queue_start']
        request['daemon_start'] = kwargs['daemon_start']
        request['application_start'] = kwargs['application_start']

    elif name == 'request_finished':
        request = mod_wsgi.request_data()

        timestamp = int(request['application_start'] * 1000000000)

        samples = []

        item = {}
        item['time'] = timestamp
        item['measurement'] = 'request'

        fields = {}

        fields['application_time'] = kwargs.get('application_time')

        fields['cpu_user_time'] = kwargs.get('cpu_user_time')
        fields['cpu_system_time'] = kwargs.get('cpu_system_time')
        fields['output_length'] = kwargs.get('output_length')

        cpu_user_time = kwargs.get('cpu_user_time')
        cpu_system_time = kwargs.get('cpu_system_time')
        application_time = kwargs.get('application_time')

        if application_time:
            cpu_burn = (cpu_user_time + cpu_system_time) / application_time
            fields['cpu_burn'] = cpu_burn

        fields['queue_time'] = (request['application_start'] -
                request['request_start'])

        item['fields'] = fields
        samples.append(item)

        #print('SAMPLES', samples)

        influxdb_client_1.write_points(samples)

        #print('REQUEST', request)
        #print('FINISH', time.time()-request['start_time'])
        #print('PROCESS', mod_wsgi.process_metrics()) 
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

    for i in range(10000):
      i**2

    #time.sleep(0.01)

    try:
        yield output

        if 'yield' in failure_mode:
            raise RuntimeError('yield')
    finally:
        if 'close' in failure_mode:
            raise RuntimeError('close')
