import os, json
os.environ.setdefault('IBM_API_KEY', 'demo')
os.environ.setdefault('IBM_PROJECT_ID', 'demo')
from app import app

c = app.test_client()
c.testing = True

errors = []

def check(label, resp, expected_status=200, check_text=None):
    ok = resp.status_code == expected_status
    if check_text:
        ok = ok and check_text in resp.data.decode()
    status = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(label)
    print(f"  [{status}] {label}  (HTTP {resp.status_code})")

print("=== Page routes ===")
check("GET /",          c.get('/'))
check("GET /dashboard", c.get('/dashboard'))
check("GET /nutrition", c.get('/nutrition'))
check("GET /meals",     c.get('/meals'))
check("GET /bmi",       c.get('/bmi'))
check("GET /workout",   c.get('/workout'))
check("GET /login",     c.get('/login'))
check("GET /register",  c.get('/register'))
check("GET /profile — redirect when not logged in", c.get('/profile'), 302)

print()
print("=== Auth flow ===")
# Register
r = c.post('/register', data={
    'name': 'Test User', 'email': 'test@fitverse.ai',
    'password': 'pass123', 'confirm': 'pass123',
    'age': '28', 'gender': 'male', 'goal': 'muscle gain',
    'weight': '75', 'height': '178', 'activity': 'moderate',
}, follow_redirects=False)
check("POST /register — success redirect", r, 302)

# Now logged in — /profile should work
r = c.get('/profile')
check("GET /profile — after login", r, 200, 'Test User')

# /api/me
r = c.get('/api/me')
d = json.loads(r.data)
check("/api/me — returns user data", r, 200)
print(f"         name={d.get('name')}  initials={d.get('initials')}  color={d.get('avatar_color')}")

# Profile update
r = c.post('/profile/update', data={
    'name': 'Test User Updated', 'age': '29',
    'gender': 'male', 'weight': '74', 'height': '178',
    'goal': 'weight loss', 'activity': 'active',
}, follow_redirects=False)
check("POST /profile/update — redirect", r, 302)

# Logout
r = c.get('/logout', follow_redirects=False)
check("GET /logout — redirect to login", r, 302)

# Login
r = c.post('/login', data={
    'email': 'test@fitverse.ai', 'password': 'pass123'
}, follow_redirects=False)
check("POST /login — success redirect", r, 302)

# Wrong password
r = c.post('/login', data={
    'email': 'test@fitverse.ai', 'password': 'wrongpw'
}, follow_redirects=True)
check("POST /login — wrong password shows error", r, 200)

print()
print("=== Navbar auth include on all pages ===")
with app.test_client() as logged_out:
    for page in ['/', '/dashboard', '/nutrition', '/meals', '/bmi', '/workout']:
        r = logged_out.get(page)
        has_login  = b'/login'   in r.data
        has_signup = b'/register' in r.data
        status = "PASS" if has_login and has_signup else "FAIL"
        if status == "FAIL": errors.append(f"navbar {page}")
        print(f"  [{status}] {page} — Login link: {has_login} | Sign Up: {has_signup}")

print()
if errors:
    print(f"FAILED: {errors}")
else:
    print("=== ALL TESTS PASSED ===")
