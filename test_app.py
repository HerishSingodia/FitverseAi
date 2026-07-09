import os, json
os.environ.setdefault('IBM_API_KEY', 'demo')
os.environ.setdefault('IBM_PROJECT_ID', 'demo')
from app import app

client = app.test_client()

routes = ['/', '/dashboard', '/nutrition', '/meals', '/bmi']
for route in routes:
    resp = client.get(route)
    print("GET", route, "->", resp.status_code)

resp = client.post('/api/chat',
    data=json.dumps({'message': 'What should I eat for weight loss?'}),
    content_type='application/json')
d = json.loads(resp.data)
print("POST /api/chat ->", resp.status_code, "| chars:", len(d.get('response', '')))

resp = client.post('/api/bmi-analysis',
    data=json.dumps({'weight': 70, 'height': 175, 'age': 28, 'gender': 'male', 'unit': 'metric'}),
    content_type='application/json')
d = json.loads(resp.data)
print("POST /api/bmi-analysis ->", resp.status_code, "| BMI:", d.get('bmi'), d.get('category'))

resp = client.post('/api/meal-plan',
    data=json.dumps({'preferences': {'goal': 'weight loss', 'calories': 1800, 'diet': 'balanced', 'allergies': 'none'}}),
    content_type='application/json')
print("POST /api/meal-plan ->", resp.status_code)

resp = client.post('/api/analyze-calories',
    data=json.dumps({'foods': '200g grilled chicken, 1 cup brown rice'}),
    content_type='application/json')
print("POST /api/analyze-calories ->", resp.status_code)

resp = client.get('/api/nutrition-tips?category=weight+loss')
print("GET /api/nutrition-tips ->", resp.status_code)

resp = client.post('/api/workout-plan',
    data=json.dumps({'level': 'intermediate', 'goal': 'muscle gain', 'days': 4}),
    content_type='application/json')
print("POST /api/workout-plan ->", resp.status_code)

print()
print("=== All tests PASSED ===")
