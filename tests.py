import json
import unittest
from server import application
from io import BytesIO

class TestApp(unittest.TestCase):
    
    def simulate_request(self, path, method='GET', data=None):
        environ = {
            'PATH_INFO': path,
            'REQUEST_METHOD': method,
        }
        
        if data:
            data = json.dumps(data).encode('utf-8')
            environ['CONTENT_LENGTH'] = str(len(data))
            environ['wsgi.input'] = BytesIO(data)
        else:
            environ['CONTENT_LENGTH'] = '0'
            environ['wsgi.input'] = BytesIO(b'')
        
        def start_response(status, headers):
            self.status = status
            self.headers = headers
        
        response = application(environ, start_response)
        return b''.join(response).decode('utf-8')
    
    def test_get_current_time_gmt(self):
        response = self.simulate_request('/')
        self.assertIn('Time in GMT:', response)
    
    def test_get_current_time_with_timezone(self):
        response = self.simulate_request('/Europe/Moscow')
        self.assertIn('Time in Europe/Moscow:', response)
    
    def test_convert_time(self):
        data = {
            'date': '12.20.2021 22:21:05',
            'tz': 'EST',
            'target_tz': 'Europe/Moscow'
        }
        response = self.simulate_request('/api/v1/convert', method='POST', data=data)
        self.assertIn('converted_time', response)
    
    def test_date_diff(self):
        data = {
            'first_date': '12.06.2024 22:21:05',
            'first_tz': 'EST',
            'second_date': '01.02.2024 12:30:00',
            'second_tz': 'Europe/Moscow'
        }
        response = self.simulate_request('/api/v1/datediff', method='POST', data=data)
        self.assertIn('difference', response)

if __name__ == '__main__':
    unittest.main()
