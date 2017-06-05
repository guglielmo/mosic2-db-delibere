import json
import requests


# test locally or with remote service_url
service_url = "http://localhost:8000"
password = 'guglielmo'

#service_url = "http://area-riservata.mosic2.celata.com"
#password = 'cowpony-butter-vizor'

print("Retrieving token for user mosic")
r = requests.post(
    '{0}/api/token-auth/'.format(service_url),
    {"username": "guglielmo", "password": password}
)
jwt_token = r.json()['token']
print(r)
print(jwt_token)
print("")

print("Rimozione della delibera")
response = requests.delete(
    '{0}/delibere/2016071'.format(service_url),
    headers={'Authorization': 'JWT ' + jwt_token}
)
print(response)
print("")


print("Creating delibera from json")
with open('./resources/fixtures/delibera.json'.format(service_url), 'r') as f:
        delibera = json.load(f)
response = requests.post(
    '{0}/delibere'.format(service_url),
    json=delibera,
    headers={'Authorization': 'JWT ' + jwt_token}
)
print(response)
print("")

print("Uploading Delibera file")
response = requests.put(
    '{0}/upload_file/docs/2016/E160071.pdf'.format(service_url),
    files={'file': open('./resources/fixtures/E160071.pdf', 'rb')},
    headers={'Authorization': 'JWT ' + jwt_token}
)
print(response)
print("")

print("Uploading file with no corresponding record in DB")
response = requests.put(
    '{0}/upload_file/documents/E160071.pdf'.format(service_url),
    files={'file': open('./resources/fixtures/E160071.pdf', 'rb')},
    headers={'Authorization': 'JWT ' + jwt_token}
)
print(response)
print("")


print("Retrieving full delibera")
response = requests.get(
    '{0}/delibere/2016071'.format(service_url),
    headers={'Authorization': 'JWT ' + jwt_token}
)
print(response)

print(response.json())

