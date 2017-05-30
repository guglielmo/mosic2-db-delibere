import json

from django.test import TestCase
from rest_framework.test import RequestsClient


class RequestTest(TestCase):

    def setUp(self):
        """
        create client_stub and load users and groups from fixtures
        contenttypes, sites, and permissions are already in test db
        
        so, in order to create users and group, it is sufficient to invoke:
        python project/manage.py dumpdata --natural-foreign \
          --exclude=auth.permission auth \
          --indent=4 > resources/fixtures/setup.json
        
        :return:
        """
        from django.core.management import call_command
        call_command("loaddata", "setup", verbosity=0)
        self.client_stub = RequestsClient()


    def test_create_seduta(self):
        with open('./resources/fixtures/delibera.json', 'r') as f:
            delibera = json.load(f)

        r = self.client_stub.post(
            'http://localhost:8000/api-token-auth/',
            data={"username": "guglielmo", "password": "guglielmo"}
        ).json()


        response = self.client_stub.post(
            'http://localhost:8000/delibere',
            json=delibera,
            headers={'Authorization': 'JWT ' + r['token']}
        )
        self.assertEquals(response.status_code, 201)

        response = self.client_stub.put(
            'http://localhost:8000/upload_file/docs/2016/E160071.pdf',
            files={'file': open('./resources/fixtures/E160071.pdf', 'rb')},
            headers={'Authorization': 'JWT ' + r['token']}
        )
        self.assertEquals(response.status_code, 204)

        response = self.client_stub.put(
            'http://localhost:8000/upload_file/docs/JWTHandbook.pdf',
            files={'file': open('./resources/fixtures/E160072.pdf', 'rb')},
            headers={'Authorization': 'JWT ' + r['token']}
        )
        self.assertEquals(response.status_code, 404)

        response = self.client_stub.get(
            'http://localhost:8000/delibere/2016071',
            headers={'Authorization': 'JWT ' + r['token']}
        )
        self.assertEquals(response.status_code, 200)

        response = self.client_stub.delete(
            'http://localhost:8000/delibere/2016071',
            headers={'Authorization': 'JWT ' + r['token']}
        )
        self.assertEquals(response.status_code, 204)

