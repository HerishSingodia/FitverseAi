import os
import json
import re
import hashlib
import uuid
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fitverse-ai-secret-2024")

# ─── In-memory user store (replace with a real DB in production) ──────────────
# Structure: { email: { id, name, email, password_hash, avatar_color,
#               age, gender, weight, height, goal, activity, joined } }
USERS: dict = {}

# ─── Auth helpers ─────────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def current_user() -> dict | None:
    email = session.get("user_email")
    return USERS.get(email) if email else None

# ─── Avatar colour palette ─────────────────────────────────────────────────────
AVATAR_COLORS = ["#6366f1","#10b981","#f59e0b","#ef4444","#06b6d4","#8b5cf6","#ec4899"]

# ─── IBM watsonx.ai Configuration ─────────────────────────────────────────────
IBM_API_KEY   = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "")
IBM_REGION    = os.getenv("IBM_REGION", "us-south")

REGION_URLS = {
    "us-south": "https://us-south.ml.cloud.ibm.com",
    "eu-de":    "https://eu-de.ml.cloud.ibm.com",
    "eu-gb":    "https://eu-gb.ml.cloud.ibm.com",
    "jp-tok":   "https://jp-tok.ml.cloud.ibm.com",
    "au-syd":   "https://au-syd.ml.cloud.ibm.com",
}
IBM_URL = REGION_URLS.get(IBM_REGION, "https://us-south.ml.cloud.ibm.com")

# ─── watsonx Model Helper ──────────────────────────────────────────────────────
def get_watsonx_model(model_id: str = "ibm/granite-13b-instruct-v2") -> ModelInference:
    credentials = Credentials(
        url=IBM_URL,
        api_key=IBM_API_KEY,
    )
    client = APIClient(credentials)
    model = ModelInference(
        model_id=model_id,
        api_client=client,
        project_id=IBM_PROJECT_ID,
        params={
            GenParams.MAX_NEW_TOKENS: 900,
            GenParams.MIN_NEW_TOKENS: 30,
            GenParams.TEMPERATURE:    0.7,
            GenParams.TOP_P:          0.9,
            GenParams.TOP_K:          50,
            GenParams.REPETITION_PENALTY: 1.1,
        },
    )
    return model


def ask_granite(prompt: str, model_id: str = "ibm/granite-13b-instruct-v2") -> str:
    """Send a prompt to IBM Granite and return the generated text."""
    demo_keys = {"", "your_ibm_api_key_here", "demo"}
    if not IBM_API_KEY or IBM_API_KEY.strip() in demo_keys:
        return _demo_response(prompt)
    try:
        model = get_watsonx_model(model_id)
        result = model.generate_text(prompt=prompt)
        return result.strip() if isinstance(result, str) else result.get("results", [{}])[0].get("generated_text", "").strip()
    except Exception as exc:
        app.logger.error("watsonx error: %s", exc)
        return _demo_response(prompt)


def _demo_response(prompt: str) -> str:
    """Fallback demo responses when no API key is configured."""
    p = prompt.lower()
    if "bmi" in p or "body mass" in p:
        return (
            "Based on your BMI calculation, here's a comprehensive health overview:\n\n"
            "**BMI Interpretation & Recommendations:**\n"
            "• A healthy BMI range is 18.5–24.9\n"
            "• Focus on balanced nutrition with whole foods\n"
            "• Aim for 150 min of moderate exercise per week\n"
            "• Stay hydrated — 8 glasses of water daily\n"
            "• Prioritize 7–9 hours of quality sleep\n\n"
            "**Personalized Action Plan:**\n"
            "1. Start with a calorie-deficit of 300–500 kcal/day if needed\n"
            "2. Include protein at every meal (chicken, legumes, eggs)\n"
            "3. Add strength training 2–3x per week\n"
            "4. Track your progress weekly, not daily"
        )
    if "meal" in p or "plan" in p or "diet" in p:
        return (
            "**Personalized 7-Day Meal Plan:**\n\n"
            "🌅 **Breakfast Options:**\n"
            "• Overnight oats with berries & chia seeds (380 kcal)\n"
            "• Greek yogurt parfait with granola (320 kcal)\n"
            "• Avocado toast with poached eggs (410 kcal)\n\n"
            "🌞 **Lunch Options:**\n"
            "• Grilled chicken salad with quinoa (450 kcal)\n"
            "• Lentil soup with whole-grain bread (400 kcal)\n"
            "• Turkey & veggie wrap (420 kcal)\n\n"
            "🌙 **Dinner Options:**\n"
            "• Baked salmon with roasted vegetables (520 kcal)\n"
            "• Stir-fry tofu with brown rice (480 kcal)\n"
            "• Lean beef bowl with sweet potato (550 kcal)\n\n"
            "💡 **Snack Ideas:** Apple + almond butter · Hummus + carrots · Mixed nuts"
        )
    if "calor" in p or "nutrition" in p or "food" in p:
        return (
            "**Nutritional Analysis & Calorie Breakdown:**\n\n"
            "📊 **Macronutrient Distribution:**\n"
            "• Protein: 30% (builds & repairs muscle)\n"
            "• Carbohydrates: 45% (primary energy source)\n"
            "• Healthy Fats: 25% (hormones & brain health)\n\n"
            "🥦 **Top Nutrient-Dense Foods:**\n"
            "• Spinach — 7 kcal/cup, rich in iron & vitamins\n"
            "• Salmon — 208 kcal/100g, omega-3 powerhouse\n"
            "• Quinoa — 222 kcal/cup, complete protein\n"
            "• Blueberries — 84 kcal/cup, antioxidant-rich\n\n"
            "⚡ **Daily Calorie Tips:**\n"
            "1. Eat every 3–4 hours to maintain metabolism\n"
            "2. Front-load calories earlier in the day\n"
            "3. Post-workout: protein + carb within 30 min"
        )
    if "workout" in p or "exercise" in p or "fitness" in p:
        return (
            "**Personalized Fitness & Workout Plan:**\n\n"
            "💪 **Weekly Training Split:**\n"
            "• Mon/Thu: Upper body strength (chest, back, shoulders)\n"
            "• Tue/Fri: Lower body strength (quads, hamstrings, glutes)\n"
            "• Wed: Active recovery (yoga, stretching, 30-min walk)\n"
            "• Sat: HIIT cardio (20 min, 40s on / 20s rest)\n"
            "• Sun: Full rest & recovery\n\n"
            "🔥 **Calorie Burn Estimates:**\n"
            "• Strength training: 200–300 kcal/hr\n"
            "• HIIT cardio: 400–600 kcal/hr\n"
            "• Yoga/stretching: 150–200 kcal/hr\n\n"
            "⚡ **Progressive Overload:** Increase weight or reps by 5% every 2 weeks"
        )
    return (
        "As your AI nutrition coach, I'm here to help you achieve your wellness goals! "
        "I can assist with:\n\n"
        "🥗 **Nutrition Planning** — personalized meal plans & calorie tracking\n"
        "💪 **Fitness Guidance** — workout routines & exercise tips\n"
        "📊 **BMI Analysis** — health metrics & body composition\n"
        "🍎 **Food Insights** — calorie counts & nutrient breakdowns\n"
        "🧘 **Wellness Tips** — sleep, hydration & stress management\n\n"
        "Ask me anything about your health journey!"
    )


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")


@app.route("/meals")
def meals():
    return render_template("meals.html")


@app.route("/bmi")
def bmi():
    return render_template("bmi.html")


@app.route("/workout")
def workout():
    return render_template("workout.html")


# ─── Auth Routes ──────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("profile"))
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")
        age      = request.form.get("age", "25")
        gender   = request.form.get("gender", "male")
        goal     = request.form.get("goal", "weight loss")

        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if email in USERS:
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # Create user
        color = AVATAR_COLORS[len(USERS) % len(AVATAR_COLORS)]
        USERS[email] = {
            "id":            str(uuid.uuid4())[:8],
            "name":          name,
            "email":         email,
            "password_hash": _hash(password),
            "avatar_color":  color,
            "initials":      "".join(p[0].upper() for p in name.split()[:2]),
            "age":           age,
            "gender":        gender,
            "weight":        request.form.get("weight", ""),
            "height":        request.form.get("height", ""),
            "goal":          goal,
            "activity":      request.form.get("activity", "moderate"),
            "joined":        datetime.utcnow().strftime("%B %Y"),
            "streak":        0,
            "workouts_done": 0,
            "calories_tracked": 0,
        }
        session["user_email"] = email
        flash(f"Welcome to FitVerse AI, {name}! 🎉", "success")
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("profile"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember")
        user     = USERS.get(email)
        if not user or user["password_hash"] != _hash(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        session["user_email"] = email
        if remember:
            session.permanent = True
        flash(f"Welcome back, {user['name']}! 💪", "success")
        return redirect(url_for("profile"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    name = current_user().get("name", "User") if current_user() else "User"
    session.pop("user_email", None)
    flash(f"Goodbye, {name}! See you soon. 👋", "info")
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    user = current_user()
    return render_template("profile.html", user=user)


@app.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    email = session["user_email"]
    user  = USERS[email]
    user["name"]     = request.form.get("name", user["name"]).strip()
    user["age"]      = request.form.get("age", user["age"])
    user["gender"]   = request.form.get("gender", user["gender"])
    user["weight"]   = request.form.get("weight", user["weight"])
    user["height"]   = request.form.get("height", user["height"])
    user["goal"]     = request.form.get("goal", user["goal"])
    user["activity"] = request.form.get("activity", user["activity"])
    user["initials"] = "".join(p[0].upper() for p in user["name"].split()[:2])
    # Password change (optional)
    new_pw = request.form.get("new_password", "").strip()
    if new_pw:
        if len(new_pw) < 6:
            flash("New password must be at least 6 characters.", "danger")
            return redirect(url_for("profile"))
        user["password_hash"] = _hash(new_pw)
    flash("Profile updated successfully! ✅", "success")
    return redirect(url_for("profile"))


# ─── API: Current user (for navbar JS) ────────────────────────────────────────
@app.route("/api/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in":    True,
        "name":         user["name"],
        "initials":     user["initials"],
        "avatar_color": user["avatar_color"],
        "email":        user["email"],
    })


# ─── API Endpoints ─────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400

    prompt = (
        "You are FitVerse AI, an expert nutrition coach and wellness advisor. "
        "Provide detailed, actionable, and motivating advice. "
        "Format responses with clear sections and bullet points.\n\n"
        f"User: {message}\n\nFitVerse AI:"
    )
    reply = ask_granite(prompt)
    return jsonify({"response": reply, "status": "success"})


@app.route("/api/analyze-calories", methods=["POST"])
def api_analyze_calories():
    data = request.get_json(silent=True) or {}
    food_items = data.get("foods", "").strip()
    if not food_items:
        return jsonify({"error": "Food items are required"}), 400

    prompt = (
        "You are a professional nutritionist. Analyze these food items and provide "
        "detailed calorie counts, macronutrients (protein, carbs, fats), and health scores.\n\n"
        f"Food items: {food_items}\n\n"
        "Provide a structured breakdown with total calories, macros, and health tips:"
    )
    analysis = ask_granite(prompt)
    return jsonify({"analysis": analysis, "status": "success"})


@app.route("/api/meal-plan", methods=["POST"])
def api_meal_plan():
    data = request.get_json(silent=True) or {}
    preferences = data.get("preferences", {})
    goal        = preferences.get("goal", "weight loss")
    calories    = preferences.get("calories", 2000)
    diet_type   = preferences.get("diet", "balanced")
    allergies   = preferences.get("allergies", "none")

    prompt = (
        f"Create a detailed 7-day meal plan for someone with these preferences:\n"
        f"• Goal: {goal}\n"
        f"• Daily calories: {calories} kcal\n"
        f"• Diet type: {diet_type}\n"
        f"• Allergies/restrictions: {allergies}\n\n"
        "Include breakfast, lunch, dinner, and snacks for each day with calorie counts:"
    )
    plan = ask_granite(prompt)
    return jsonify({"plan": plan, "status": "success"})


@app.route("/api/bmi-analysis", methods=["POST"])
def api_bmi_analysis():
    data   = request.get_json(silent=True) or {}
    weight = float(data.get("weight", 0))
    height = float(data.get("height", 0))
    age    = int(data.get("age", 25))
    gender = data.get("gender", "male")
    unit   = data.get("unit", "metric")

    if unit == "imperial":
        weight_kg = weight * 0.453592
        height_m  = height * 0.0254
    else:
        weight_kg = weight
        height_m  = height / 100

    if height_m <= 0:
        return jsonify({"error": "Invalid height"}), 400

    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        color    = "#60a5fa"
    elif bmi < 25:
        category = "Normal Weight"
        color    = "#34d399"
    elif bmi < 30:
        category = "Overweight"
        color    = "#fbbf24"
    else:
        category = "Obese"
        color    = "#f87171"

    # Harris-Benedict BMR
    if gender == "male":
        bmr = 88.362 + (13.397 * weight_kg) + (482.861 * height_m) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight_kg) + (309.893 * height_m) - (4.330 * age)

    prompt = (
        f"As a fitness expert, provide a comprehensive health analysis for:\n"
        f"• BMI: {bmi} ({category})\n"
        f"• Age: {age}, Gender: {gender}\n"
        f"• Weight: {weight_kg:.1f} kg, Height: {height_m*100:.0f} cm\n"
        f"• BMR: {bmr:.0f} kcal/day\n\n"
        "Give specific recommendations for diet, exercise, and lifestyle improvements:"
    )
    advice = ask_granite(prompt)

    return jsonify({
        "bmi":      bmi,
        "category": category,
        "color":    color,
        "bmr":      round(bmr),
        "tdee": {
            "sedentary":   round(bmr * 1.2),
            "light":       round(bmr * 1.375),
            "moderate":    round(bmr * 1.55),
            "active":      round(bmr * 1.725),
            "very_active": round(bmr * 1.9),
        },
        "advice":   advice,
        "status":   "success",
    })


@app.route("/api/nutrition-tips", methods=["GET"])
def api_nutrition_tips():
    category = request.args.get("category", "general")
    prompt = (
        f"Give 5 expert nutrition and wellness tips for the category: {category}. "
        "Make them specific, actionable, science-backed, and motivating. "
        "Format as a numbered list with brief explanations:"
    )
    tips = ask_granite(prompt)
    return jsonify({"tips": tips, "category": category, "status": "success"})


@app.route("/api/workout-plan", methods=["POST"])
def api_workout_plan():
    data     = request.get_json(silent=True) or {}
    fitness_level = data.get("level", "beginner")
    goal     = data.get("goal", "weight loss")
    days     = data.get("days", 4)

    prompt = (
        f"Create a {days}-day workout plan for a {fitness_level} with goal: {goal}.\n"
        "Include exercise names, sets, reps, rest periods, and calorie estimates. "
        "Make it progressive and achievable:"
    )
    plan = ask_granite(prompt)
    return jsonify({"plan": plan, "level": fitness_level, "goal": goal, "status": "success"})


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
