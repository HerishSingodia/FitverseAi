from dotenv import load_dotenv; load_dotenv()
import os, requests

api_key = os.getenv('IBM_API_KEY')

# Get IAM token
print('Getting IAM token...')
resp = requests.post(
    'https://iam.cloud.ibm.com/identity/token',
    data={'grant_type': 'urn:ibm:params:oauth:grant-type:apikey', 'apikey': api_key},
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
token = resp.json().get('access_token')
print('IAM token: OK (HTTP', resp.status_code, ')')
print()

# Try each region
regions = ['us-south', 'eu-de', 'eu-gb', 'jp-tok', 'au-syd']
found_any = False
for region in regions:
    url = 'https://' + region + '.ml.cloud.ibm.com/v2/projects?limit=10'
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    if r.status_code == 200:
        projects = r.json().get('resources', [])
        if projects:
            found_any = True
            print('Region:', region)
            for p in projects:
                pid  = p['metadata']['id']
                name = p['entity']['name']
                print('  Project ID :', pid)
                print('  Name       :', name)
                print()
        else:
            print('Region:', region, '-> no projects found')
    else:
        print('Region:', region, '->', r.status_code)

if not found_any:
    print()
    print('No watsonx.ai projects found.')
    print('You may need to create one at https://dataplatform.cloud.ibm.com')
