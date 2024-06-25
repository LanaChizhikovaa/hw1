import json
from datetime import datetime
from pytz import timezone, all_timezones, utc
from wsgiref.simple_server import make_server

def get_current_time(tz_name):
    if tz_name not in all_timezones:
        tz_name = 'GMT'
    tz = timezone(tz_name)
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')

def convert_time(data):
    try:
        date_str = data['date']
        tz_from = data['tz']
        tz_to = data['target_tz']
        date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
        from_tz = timezone(tz_from)
        to_tz = timezone(tz_to)
        date = from_tz.localize(date)
        converted_date = date.astimezone(to_tz)
        return converted_date.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as e:
        return str(e)

def date_diff(data):
    try:
        first_date_str = data['first_date']
        first_tz_name = data['first_tz']
        second_date_str = data['second_date']
        second_tz_name = data['second_tz']
        
        first_tz = timezone(first_tz_name)
        second_tz = timezone(second_tz_name)
        
        first_date = first_tz.localize(datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S'))
        second_date = second_tz.localize(datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d'))
        
        diff = (second_date - first_date).total_seconds()
        return str(int(diff))
    except Exception as e:
        return str(e)

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    if method == 'GET' and (path == '' or path in all_timezones):
        tz_name = path if path else 'GMT'
        current_time = get_current_time(tz_name)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [f"<html><body><h1>Time in {tz_name}: {current_time}</h1></body></html>".encode('utf-8')]
    
    if method == 'POST' and path == 'api/v1/convert':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            converted_time = convert_time(data)
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({'converted_time': converted_time}).encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]
    
    if method == 'POST' and path == 'api/v1/datediff':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            difference = date_diff(data)
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({'difference': difference}).encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]
    
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

if __name__ == '__main__':
    port = 8000
    with make_server('', port, application) as server:
        print(f"Serving on {port}...")
        server.serve_forever()
