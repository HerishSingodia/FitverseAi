# FitVerse AI — IBM watsonx.ai Nutrition & Wellness Platform

A production-ready, AI-powered wellness web application built with **Python Flask** and **IBM watsonx.ai Granite Foundation Models**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Chat Coach | Real-time nutrition & fitness coaching via IBM Granite |
| 🍎 Calorie Analyzer | Full macro + micro-nutrient breakdown for any meal |
| 📅 7-Day Meal Planner | Personalized meal plans with calorie targets |
| 📊 BMI Calculator | BMI, BMR, TDEE with AI-powered health advice |
| 💪 Workout Generator | AI-crafted workout routines for any fitness level |
| 📈 Dashboard | Weekly calorie charts, goal progress, KPI cards |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo>
cd FitverseAi
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your IBM Cloud credentials:

```env
IBM_API_KEY=your_actual_api_key
IBM_PROJECT_ID=your_watsonx_project_id
IBM_REGION=us-south
FLASK_SECRET_KEY=your_secret_key
```

### 3. Run the Application

```bash
python app.py
```

Visit **http://localhost:5000**

---

## 🔑 Getting IBM watsonx.ai Credentials

1. Sign up at [IBM Cloud](https://cloud.ibm.com)
2. Create a **watsonx.ai** service instance
3. Go to **Manage → Access (IAM) → API Keys** → Create API Key
4. Copy your **Project ID** from watsonx.ai Studio

> **No API key?** The app works in demo mode with pre-built responses — perfect for UI testing.

---

## 🏗 Project Structure

```
FitverseAi/
├── app.py                    # Flask app + IBM watsonx.ai integration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── Procfile                  # Gunicorn deployment config
├── templates/
│   ├── index.html            # Landing page with AI chat demo
│   ├── dashboard.html        # Analytics dashboard + AI coach
│   ├── nutrition.html        # Calorie & nutrition analyzer
│   ├── meals.html            # 7-day meal plan generator
│   └── bmi.html              # BMI / BMR / TDEE calculator
└── static/
    ├── css/style.css         # Dark theme, glassmorphism, animations
    └── js/main.js            # Scroll animations, nav utils
```

---

## 🤖 AI Models Used

| Model | Use Case |
|---|---|
| `ibm/granite-13b-instruct-v2` | General nutrition coaching, meal plans, BMI advice |

All requests are routed through your own IBM Cloud account — your data never leaves your environment.

---

## 🛡 Security

- IBM API key stored in `.env` (never committed to source control)
- `.env` is excluded via `.gitignore`
- All AI requests authenticated server-side via IBM IAM

---

## 📦 Deploy to IBM Cloud Code Engine / Heroku

```bash
# IBM Code Engine
ibmcloud ce app create --name fitverse-ai --image <your-image>

# Heroku
heroku create fitverse-ai
heroku config:set IBM_API_KEY=xxx IBM_PROJECT_ID=yyy
git push heroku main
```

---

## 🧰 Tech Stack

- **Backend**: Python 3.10+, Flask 3.0, Gunicorn
- **AI**: IBM watsonx.ai, Granite Foundation Models
- **Frontend**: Bootstrap 5.3, Font Awesome 6, Bootstrap Icons
- **Charts**: Chart.js 4
- **Styling**: CSS3 glassmorphism, CSS animations, CSS variables
