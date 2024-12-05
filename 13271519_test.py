import json
from urllib.request import Request, urlopen
import time, unittest
from s13271519_server import app
from urllib.error import HTTPError

SERVER = "localhost:5000"
JSON_CONTENT_TYPE = "application/json; charset=UTF-8"

#POST request http://localhost:5000/pi
def do_pi(username, password, simulations, concurrency):
    data = {"username" : username,
            "password":password,
            "simulations":simulations,
            "concurrency":concurrency}
    req = Request(url = f"http://{SERVER}/pi",
            data = json.dumps(data).encode(),
            headers = {"Content-type": JSON_CONTENT_TYPE},
            method = "POST")
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    return result

#POST request http://localhost:5000/legacy_pi
def do_legacy_pi(username, password, protocol, concurrency):
    data = {"username" : username,
            "password":password,
            "protocol":protocol,
            "concurrency":concurrency}
    req = Request(url = f"http://{SERVER}/legacy_pi",
            data = json.dumps(data).encode(),
            headers = {"Content-type": JSON_CONTENT_TYPE},
            method = "POST")
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    return result

#POST request http://localhost:5000/statistics
def do_statistics(username, password):
    data = {"username" : username,
            "password":password}
    req = Request(url = f"http://{SERVER}/statistics",
            data = json.dumps(data).encode(),
            headers = {"Content-type": JSON_CONTENT_TYPE},
            method = "POST")
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    return result

#Unittest
class TestdopiServer(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True
    
    #Test `/pi` with with correct data
    def test_do_pi_Success(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "simulations": 1000000,
            "concurrency": 8
        }
        response = self.app.post('/pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('PI', response.json)
        self.assertIn('execution_time', response.json)

    #Test `/pi` with invalid user name
    def test_do_pi_username(self):
        data = {
            "username": "0001",
            "password": "0000-pw",
            "simulations": 1000000,
            "concurrency": 8
        }
        response = self.app.post('/pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "user info error")

    #Tests `/pi` with an invalid password.
    def test_do_pi_password(self):
        data = {
            "username": "0000",
            "password": "0001-pw",
            "simulations": 1000000,
            "concurrency": 8
        }
        response = self.app.post('/pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "user info error")

    #Tests `/pi` with missing simulations.
    def test_do_pi_simulations1(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "simulations": "",
            "concurrency": 8
        }
        response = self.app.post('/pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "missing field simulations")

    #Tests `/pi` with invalid simulations.
    def test_do_pi_simulations2(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "simulations": "99",
            "concurrency": 8
        }
        response = self.app.post('/pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "invalid field simulations")

    #Tests `/pi` with invalid concurrency.
    def test_do_pi_concurrency(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "simulations": 1000000,
            "concurrency": 9
        }
        response = self.app.post('/pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "invalid field concurrency")

    #Tests `/legacy_pi` with correct data using TCP protocol. 
    def test_do_legacy_pi_tcp_Success(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "protocol": "tcp",
            "concurrency": 8
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('PI', response.json)
        self.assertIn('execution_time', response.json)

    #Tests `/legacy_pi` with correct data using UDP protocol.
    def test_do_legacy_pi_udp_Success(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "protocol": "udp",
            "concurrency": 8
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('PI', response.json)
        self.assertIn('execution_time', response.json)

    #Tests `/legacy_pi` with an invalid user name.
    def test_do_legacy_pi_username(self):
        data = {
            "username": "0001",
            "password": "0000-pw",
            "protocol": "tcp",
            "concurrency": 8
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "user info error")

    #Tests `/legacy_pi` with an invalid password.
    def test_do_legacy_pi_password(self):
        data = {
            "username": "0000",
            "password": "0001-pw",
            "protocol": "tcp",
            "concurrency": 8
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "user info error")

    #Tests `/legacy_pi` with an missing protocol.
    def test_do_legacy_pi_protocol1(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "protocol": "",
            "concurrency": 8
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "missing field protocol")

    #Tests `/legacy_pi` with an invalid protocol.
    def test_do_legacy_pi_protocol2(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "protocol": "cp",
            "concurrency": 8
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "invalid field protocol")

    #Tests `/legacy_pi` with an invalid concurrency.
    def test_do_legacy_pi_concurrency(self):
        data = {
            "username": "0000",
            "password": "0000-pw",
            "protocol": "tcp",
            "concurrency": 9
        }
        response = self.app.post('/legacy_pi', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "invalid field concurrency")

    #Tests `/statistics` with correct data.
    def test_do_statistics_Success(self):
        data = {
            "username": "0000",
            "password": "0000-pw"
        }
        response = self.app.post('/statistics', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Count', response.json)
        self.assertIn('username', response.json)

    #Tests `/statistics` with an invalid user name.
    def test_do_statistics_username(self):
        data = {
            "username": "0001",
            "password": "0000-pw"
        }
        response = self.app.post('/statistics', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "user info error")

    #Tests `/statistics` with an invalid password.
    def test_do_statistics_password(self):
        data = {
            "username": "0000",
            "password": "0001-pw"
        }
        response = self.app.post('/statistics', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "user info error")



if __name__ == "__main__":
    print(do_pi("0000", "0000-pw", 10000000, 8))
    print(do_legacy_pi("0000", "0000-pw", "tcp", 4))
    print(do_statistics("0000", "0000-pw"))
    unittest.main()
