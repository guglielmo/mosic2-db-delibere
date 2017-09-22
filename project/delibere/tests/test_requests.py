import mock
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from delibere import search_indexes

User = get_user_model()


class RequestTestCase(TestCase):
    """Testcase class for requests

    Tests requests to create and delete a simple delibera, with no inner fields
    and a complex delibera, with inner fields and a document that is uploaded.
    """


    def setUp(self):
        """
        create test user and APIClient instance to perfotm tests with
        """

        # patching Haystack search index class
        # don't want to connect to Solr for real during tests
        patcher = mock.patch('delibere.search_indexes.DeliberaIndex')
        self.MockDeliberaIndex = patcher.start()
        self.addCleanup(patcher.stop)

        self.client = APIClient()
        self.client.force_authenticate(
            user=User.objects.create_user('test')
        )

        self.simple_delibera = {
            "data": "2016-12-01",
            "anno": "2016",
            "codice": "E160071",
            "numero": "71",
            "descrizione": "FONDO SANITARIO NAZIONALE 2007, 2008, 2009, 2010 E 2011. CONGUAGLI PER LE DIFFERENZE TRA GETTITI DI IRAP E DI ADDIZIONALE REGIONALE IRPEF EFFETTIVI E STIMATI IN SEDE DI RIPARTO DEL FONDO SANITARIO NAZIONALE. REGIONE SICILIANA",
            "cc_data": "2017-02-22",
            "cc_registro": "",
            "cc_foglio": "195",
            "gu_data": "2017-03-08",
            "gu_numero": "56",
            "gu_tipologia": "ORD",
        }
        self.complex_delibera = {
            "id": 10514,
            "slug": "32-13-marzo-1996",
            "codice": "E160071",
            "descrizione": "REVOCHE DI FINANZIAMENTI PER INTERVENTI AMBIENTALI AI SENSI DELLA LEGGE 493/93 -REGIONE ABRUZZO-",
            "firmatario": {
                "id": 32,
                "nominativo": "ARCELLI"
            },
            "data": "1996-03-13",
            "anno": "1996",
            "numero": "32",
            "cc_data": "1996-04-30",
            "cc_registro": "1",
            "cc_foglio": "95",
            "gu_data": "1997-05-21",
            "gu_numero": "117",
            "gu_tipologia": "I",
            "documenti": [
                {
                    "nome": "E160071.doc",
                    "estensione": "DOC",
                    "tipo_documento": "P",
                    "file": "docs/2016/E160071.doc"
                }
            ],
            "settori": [
                {
                    "descrizione": "Ambiente",
                }
            ],
            "amministrazioni": [
                {
                    "codice": "19",
                    "denominazione": "Ministero dell'ambiente"
                }
            ],
            "normative": [
                {
                    "id": 11,
                    "descrizione": "D.L. 398/1993 CVT. L. 493/1993"
                }
            ]
        }

    def test_upload_non_existing_doc_gives_404(self):
        assert search_indexes.DeliberaIndex is self.MockDeliberaIndex

        with open('./resources/fixtures/E160072.pdf', 'rb') as fp:
            response = self.client.put(
                '/api/upload_file/docs/JWTHandbook.pdf',
                {'file': fp },
            )
            self.assertEquals(response.status_code, 404)

    def test_create_simple_delibera(self):
        assert search_indexes.DeliberaIndex is self.MockDeliberaIndex

        response = self.client.post(
            '/api/delibere', self.simple_delibera, format='json'
        )
        self.assertEquals(response.status_code, 201)

    def test_create_complex_delibera(self):
        assert search_indexes.DeliberaIndex is self.MockDeliberaIndex

        response = self.client.post(
            '/api/delibere', self.complex_delibera, format='json'
        )
        self.assertEquals(response.status_code, 201)

        with open('./resources/fixtures/E160071.pdf', 'rb') as fp:
            response = self.client.put(
                '/api/upload_file/{0}'.format(
                    self.complex_delibera['documenti'][0]['file']
                ),
                {'file': fp },
            )
            self.assertEquals(response.status_code, 204)

    def test_remove_complex_delibera(self):
        assert search_indexes.DeliberaIndex is self.MockDeliberaIndex

        inner_fields = [
            'settori', 'amministrazioni', 'normative',
            'firmatario'
        ]


        # create delibera from data
        response = self.client.post(
            '/api/delibere', self.complex_delibera, format='json'
        )
        self.assertEquals(response.status_code, 201)

        # upload document file
        with open('./resources/fixtures/E160071.pdf', 'rb') as fp:
            response = self.client.put(
                '/api/upload_file/{0}'.format(
                    self.complex_delibera['documenti'][0]['file']
                ),
                {'file': fp },
            )
            self.assertEquals(response.status_code, 204)

        # delibera can be found in list
        response = self.client.get(
            '/api/delibere', format='json'
        )
        self.assertEquals(response.data['count'], 1)
        delibera_id = response.data['results'][0]['id']

        # inner fields are not visible in list mode
        for f in inner_fields:
            self.assertEquals(f in response.data['results'][0], False)

        # delibera was created with inner fields
        response = self.client.get(
            '/api/delibere/{0}'.format(delibera_id), format='json'
        )
        for f in inner_fields:
            self.assertEquals(f in response.data, True)
            self.assertGreater(len(response.data[f]), 0)


        # file was uploaded
        uploaded_doc_path = './resources/media/{0}'.format(
            self.complex_delibera['documenti'][0]['file']
        )
        self.assertEquals(os.path.exists(uploaded_doc_path), True)

        # remove delibera
        response = self.client.delete(
                '/api/delibere/{0}'.format(delibera_id), format='json'
        )
        self.assertEquals(response.status_code, 204)

        # delibera is deleted and document removed
        response = self.client.get(
            '/api/delibere', format='json'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['count'], 0)
        self.assertEquals(os.path.exists(uploaded_doc_path), False)
