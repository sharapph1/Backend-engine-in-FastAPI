# Scalable FastAPI Production Backend & Application Engine

A high-performance, modular backend application built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, **JWT Authentication**, and **Brevo SMTP**. 

Designed using clean architecture principles with service-layer business logic separation, secure hashed OTP email verification, automated JWT access & refresh token rotation, daily streak milestone tracking, referral management, embedded WebView game metadata, and daily advertisement analytics collection.

---

## 🌟 Key Features & Capabilities

### 🔐 Authentication & Security Module
- **User Registration**: Password hashing using `pwdlib` (`Argon2id` / recommended hashing).
- **Hashed OTP Verification**: 6-digit numeric OTP hashed before database insertion. Features a 5-minute expiration timer, a 5-attempt limit counter, and automated deletion upon verification.
- **Resend OTP**: Re-issues a fresh 6-digit OTP while revoking previous active codes.
- **JWT Token Flow**: Issues JWT Access Tokens (short-lived) and Refresh Tokens (long-lived).
- **Session Control & Revocation**: Stores hashed refresh tokens in PostgreSQL for session revocation and secure user logout.

### ⚡ Daily Streaks & KYC Milestones
- **Streak Tracker**: Increments streak counter for consecutive daily logins.
- **KYC Eligibility**: Evaluates KYC status eligibility based on active consecutive streak runs.
- **Milestone Evaluation**: Evaluates tier qualifications (Silver, Gold, Diamond, Star) based on streak duration and referral counts.

### 🎁 Referral System
- **Unique Code Generation**: Automatically assigns unique 8-character alphanumeric referral identifiers to users.
- **Referral Linking**: Validates referrer codes and records unique user referral relationships.
- **Referral Analytics**: Provides detailed counts and lists of referred users.

### 🎮 WebView Games Directory
- **Game Metadata**: Serves backend-managed target URLs for native embedded WebView usage.
- **User Engagement**: Supports game liking, pinning, and gameplay session logging.
- **Engagement Metrics**: Returns real-time counts for likes, pins, and play sessions.

### 📊 Ad Impression & Daily Analytics
- **Impression Tracking**: Log daily advertisement consumption across Banner, Interstitial, Rewarded, and Native formats.
- **Daily Usage Summaries**: Tracks per-user daily ad consumption metrics.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance Python async web framework |
| **Database** | PostgreSQL | Relational database engine |
| **ORM** | SQLAlchemy 2.0 | Type-safe declarative database ORM |
| **Migrations** | Alembic | Database schema migration management |
| **Email Service** | Brevo SMTP | Transactional email delivery via `aiosmtplib` |
| **Authentication** | python-jose | JWT access and refresh token creation and parsing |
| **Hashing** | pwdlib | Hashing algorithms for passwords and OTPs |
| **Runtime** | Python 3.14 | Modern Python runtime |

---

## 📂 Project Architecture

```
app/
├── core/
│   ├── config.py           # Environment settings & Pydantic configuration
│   ├── database.py         # SQLAlchemy engine, SessionLocal, Base model
│   ├── security.py         # Password hashing, JWT tokens, get_current_user dependency
│   └── otp_security.py     # Hashed OTP utilities
├── models/
│   ├── user.py             # User model schema
│   ├── otp.py              # OTP record schema
│   ├── session.py          # Refresh token session schema
│   ├── streak.py           # Daily streak schema
│   ├── referral.py         # Referral relationship schema
│   ├── game.py             # Game metadata schema
│   ├── gameplay.py         # Gameplay tracking schema
│   ├── gamelike.py         # Game like schema
│   ├── gamepin.py          # Game pin schema
│   └── daily_usage.py      # Ad impression metrics schema
├── services/
│   ├── email_service.py    # Brevo SMTP email sender
│   ├── otp_service.py      # OTP business logic
│   ├── auth_service.py     # Authentication & JWT session logic
│   ├── streak_service.py   # Streak & milestone logic
│   ├── referral_service.py # Referral validation & stats
│   ├── game_service.py     # Game directory & engagement logic
│   └── daily_usage_service.py # Ad analytics logic
├── schemas/
│   ├── auth.py             # Auth Pydantic request/response schemas
│   ├── streak.py           # Streak Pydantic schemas
│   ├── referral.py         # Referral Pydantic schemas
│   ├── game.py             # Game Pydantic schemas
│   └── daily_usage.py      # Analytics Pydantic schemas
├── routers/
│   ├── auth.py             # /api/v1/auth endpoints
│   ├── streak.py           # /api/v1/streaks endpoints
│   ├── referral.py         # /api/v1/referrals endpoints
│   ├── game.py             # /api/v1/games endpoints
│   └── daily_usage.py      # /api/v1/analytics endpoints
├── templates/
│   └── otp_email.py        # HTML OTP transactional email template
└── main.py                 # FastAPI initialization and router wiring
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.14+
- PostgreSQL database instance
- Virtual environment (`venv`)

### 2. Environment Setup
Create a `.env` file in the project root:

```env
APP_NAME="Application Backend"
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

JWT_SECRET_KEY="your_secure_jwt_secret_key"
JWT_ALGORITHM="HS256"

ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

BREVO_SMTP_HOST="smtp-relay.brevo.com"
BREVO_SMTP_PORT=587
BREVO_SMTP_USERNAME="your_brevo_username"
BREVO_SMTP_PASSWORD="your_brevo_smtp_key"
BREVO_FROM_EMAIL="noreply@example.com"
```

### 3. Installation & Database Migrations

```bash
# Activate virtual environment
# Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### 4. Running the Application

```bash
# Start FastAPI application with Uvicorn
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access Interactive API Documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 📡 API Reference Overview

### Auth Router (`/api/v1/auth`)
- `POST /register` – Register a user and trigger OTP.
- `POST /verify-otp` – Verify hashed OTP and activate user.
- `POST /resend-otp` – Issue a new 6-digit OTP email.
- `POST /login` – Authenticate user and receive JWT tokens.
- `POST /refresh` – Exchange refresh token for a new access token.
- `POST /logout` – Revoke refresh token session.
- `GET /me` – Fetch authenticated user profile.

### Streaks Router (`/api/v1/streaks`)
- `GET /me` – Fetch current streak, KYC status, and milestone tier.
- `POST /claim` – Claim daily streak.

### Referrals Router (`/api/v1/referrals`)
- `GET /me` – Fetch referral code and list of referred friends.
- `POST /claim` – Redeem a referral code.

### Games Router (`/api/v1/games`)
- `GET /` – List active games with counts and user action flags.
- `GET /{game_id}` – Fetch game details for WebView rendering.
- `POST /` – Register a new game.
- `POST /{game_id}/like` – Toggle game like.
- `POST /{game_id}/pin` – Toggle game pin.
- `POST /{game_id}/play` – Record gameplay session.

### Analytics Router (`/api/v1/analytics`)
- `POST /ads` – Log daily ad impressions (banner, interstitial, rewarded, native).
- `GET /me` – Retrieve today's ad consumption metrics.

---

## 🧪 Testing & Verification

An automated integration script is included to verify end-to-end functionality across all modules:

```bash
python scratch/test_full_system.py
```

---

## 📄 License
This project is licensed under the MIT License.
