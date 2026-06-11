# MAX CMR — AI Companion for Memory Care & Clinical Support

> A modern Flask-based memory care companion with AI voice assistant, appointment management, clinical support workflows, and caregiver-first navigation.

## 🚀 Project Overview

`MAX CMR` is an intelligent memory care web application built with Flask. It combines a polished healthcare UI, appointment scheduling, patient-family support pages, and an AI-powered voice assistant for dementia-friendly dialog.

This repo is designed for:
- caregivers and healthcare providers supporting memory care patients
- clinic staff managing appointments, doctors, and patient workflows
- families organizing contacts, emergency support, and dementia guidance
- AI-enhanced conversations with dementia-friendly responses

## ✨ Key Features

- Flask web app with server-rendered templates and responsive UI
- Multi-page clinical support experience:
  - Home dashboard
  - Appointment booking
  - Family contacts management
  - Dementia care guidance
  - Music, games, and panic support
  - Doctor and patient dashboards
- AI voice assistant page:
  - Speech recognition
  - Google Generative AI backend for empathetic responses
  - Text-to-speech response playback
- Secure user flows with login/register and role-based navigation
- SQLite by default, optional MySQL support via environment variables
- Multi-language UI support with language selector

## 🧠 AI Readiness

The app uses `google.generativeai` to power the `/api/ask_max` endpoint and supports natural speech interaction on the `MAX AI` page. It is built to deliver simple, kind, and accessible responses for dementia care users.

## 🛠️ Tech Stack

- Python 3.x
- Flask
- SQLite / optional MySQL
- Google Generative AI SDK
- Bootstrap 5, FontAwesome, AOS, Swiper, GLightbox
- HTML, CSS, JavaScript

## 📁 Project Structure

```
App/
  app.py
  appointments.db
  static/
  templates/
.venv/
README.md
```

## ✅ Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/harishharish9693-creator/-AI-Companion-for-Memory-Care-Clinical-Support.git
   cd "final demo/final demo/demo"
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required packages:
   ```bash
   pip install Flask google-generativeai pymysql
   ```

4. Set environment variables:
   - `FLASK_SECRET_KEY` — secret key for session encryption
   - `GOOGLE_API_KEY` — Google Generative AI API key
   - Optional MySQL values if using external database:
     - `MYSQL_HOST`
     - `MYSQL_PORT`
     - `MYSQL_USER`
     - `MYSQL_PASSWORD`
     - `MYSQL_DATABASE`

5. Start the app:
   ```bash
   python App\app.py
   ```

6. Open your browser:
   ```text
   http://127.0.0.1:5000
   ```

## 🧩 Environment Variables

Use a `.env` file or your shell environment to supply:

```env
FLASK_SECRET_KEY=supersecretkey
GOOGLE_API_KEY=YOUR_GOOGLE_GENERATIVE_AI_KEY
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=secret
MYSQL_DATABASE=appointments_db
```

## 💡 Deployment Notes

This is a Flask application, so it is best deployed on platforms that support Python web servers, such as:
- Render
- Railway
- Fly.io
- Azure App Service
- PythonAnywhere

> Vercel can host static HTML/CSS/JS, but this app is a full Flask backend and is best deployed on a Python-compatible hosting provider.

## 🧪 Recommended Improvements

- Add a `requirements.txt` file
- Add database migration support with Flask-Migrate
- Harden auth and session security for production
- Add unit tests for API and authentication flows
- Add localization support for all UI text

## 📬 Contribution

If you want to improve the app, please:
- open issues for bugs or feature ideas
- submit pull requests for UI, AI behavior, or backend enhancements
- keep commits clean and well-documented

## 📎 License

Add your license statement here when ready.
