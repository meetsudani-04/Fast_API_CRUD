# 🚀 FastAPI In-Memory Trade Analyzer

A lightweight **FastAPI** application with JWT authentication, OTP-based password reset, per-user rate limiting, and a **sector analysis endpoint** that returns a **Markdown-formatted report** using the Gemini API.  
All data is stored **in-memory**, meaning it resets when the server restarts — ideal for demos and local testing.

---

## 🧩 Features

- **JWT Authentication** (signup & login)
- **OTP-based Password Reset**
- **Per-user Rate Limiting** (10 requests/minute)
- **Sector Market Analysis Reports** (Markdown output)
- **In-memory Storage** (no database needed)
- **Gemini AI Integration** for generating insights

---

## ⚙️ Prerequisites

- Python **3.10+**
- **Windows PowerShell** (commands below use PowerShell syntax)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

---

## 📦 Install Dependencies

If you already have a `requirements.txt` file:
```powershell
pip install -r requirements.txt
```

Otherwise, install manually:
```powershell
pip install fastapi uvicorn passlib[bcrypt] python-jose[cryptography] python-dotenv google-genai httpx
```

---

## 🔑 Environment Setup

Create a `.env` file in the project root directory and add the following variables:

```
SECRET_KEY=change_this_to_a_long_random_string
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ▶️ Run the API Server

```powershell
uvicorn main:app --reload
```

**Endpoints:**
- Base URL: [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- API Docs: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

---

## 📚 API Overview

**Base Path:** `/api`  
**Authentication Path:** `/api/auth`  
**Storage:** In-memory (data resets on restart)

### Endpoints

| Method | Endpoint | Description | Auth Required |
|:------:|:----------|:-------------|:---------------:|
| POST | `/api/auth/signup` | Create a new user | ❌ |
| POST | `/api/auth/login` | Login and get JWT token | ❌ |
| POST | `/api/auth/forgot-password` | Request OTP for password reset | ❌ |
| POST | `/api/auth/reset-password` | Reset password using OTP | ❌ |
| GET | `/api/get-all-users` | List all users (in-memory) | ✅ |
| GET | `/api/analyze/{sector}` | Generate sector report (Markdown) | ✅ |

---

## 🏦 Supported Sectors

```
it, banking, energy, pharma, auto, fmcg, metals, infra
```

**Rate Limit:**  
🔹 10 requests / 60 seconds per user (based on email)

---

## 🧠 Step-by-Step Usage Guide

### 1️⃣ Sign Up
```powershell
curl -X POST http://127.0.0.1:8000/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"alice@example.com\",\"password\":\"StrongPass123\"}"
```

### 2️⃣ Login to Get JWT
```powershell
curl -X POST http://127.0.0.1:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"alice@example.com\",\"password\":\"StrongPass123\"}"
```

Copy your `access_token` and set it as a PowerShell variable:
```powershell
$TOKEN = "<paste_access_token_here>"
```

### 3️⃣ Analyze a Sector (Get Markdown Report)
```powershell
curl -X GET http://127.0.0.1:8000/api/analyze/it ^
  -H "Authorization: Bearer $TOKEN"
```

Example response:
```json
{
  "report_md": "# IT Sector Analysis\n\n...markdown content..."
}
```

### 4️⃣ Save Markdown Report to File
```powershell
$resp = Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8000/api/analyze/it" -Headers @{Authorization="Bearer $TOKEN"}
$resp.report_md | Out-File -FilePath ".\it_report.md" -Encoding UTF8
```
➡ Open `it_report.md` in your editor.

### 5️⃣ Forgot / Reset Password (OTP Demo)

**Request OTP (check console for code):**
```powershell
curl -X POST http://127.0.0.1:8000/api/auth/forgot-password ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"alice@example.com\"}"
```

**Reset Password:**
```powershell
curl -X POST http://127.0.0.1:8000/api/auth/reset-password ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"alice@example.com\",\"otp_code\":\"123456\",\"new_password\":\"NewStrongPass456\"}"
```

### 6️⃣ View All Users (Admin Demo)
```powershell
curl -X GET http://127.0.0.1:8000/api/get-all-users ^
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚠️ Common Errors & Solutions

| Error | Cause | Solution |
|:------|:-------|:----------|
| **401 Unauthorized** | Missing or invalid token | Add header `Authorization: Bearer <token>` |
| **400 Invalid Sector** | Sector not allowed | Use one of the predefined sectors |
| **429 Too Many Requests** | Rate limit exceeded | Wait 1 minute and retry |
| **500 Gemini Error** | Gemini API issue | Verify your `GEMINI_API_KEY` and `.env` setup |

---

## 🗾 Notes & Limitations

- ⚡ **In-memory only** — all users and OTPs are lost after restart.  
- 🧩 **Single-process app** — multiple workers won’t share data.  
- 🔐 **OTP printed to console** — for demo only (not production safe).  
- 🔑 Keep `SECRET_KEY` **long and random** in your `.env`.

---

## 🧮 Tech Stack

| Component | Description |
|------------|-------------|
| **FastAPI** | Web framework |
| **JWT (python-jose)** | Secure user sessions |
| **Passlib (bcrypt)** | Password hashing |
| **Dotenv** | Env variable management |
| **Google GenAI** | Sector analysis content |
| **HTTPX** | Async HTTP requests |

---

> ⚙️ *This project is designed for demo and evaluation purposes only.  
For production use, replace in-memory storage with a database and secure OTP/email delivery.*

