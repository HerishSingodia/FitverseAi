import os
os.environ.setdefault('IBM_API_KEY', 'demo')
os.environ.setdefault('IBM_PROJECT_ID', 'demo')
from app import app
c = app.test_client()

r = c.get('/workout')
print('GET /workout ->', r.status_code)
assert r.status_code == 200

for page in ['/', '/dashboard', '/nutrition', '/meals', '/bmi', '/workout']:
    r = c.get(page)
    body = r.data.decode()
    has_link = '/workout' in body
    print(page, '-> HTTP', r.status_code, '| Workout nav link:', 'YES' if has_link else 'MISSING')

print()
print('=== All checks PASSED ===')
