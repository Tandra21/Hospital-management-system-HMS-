# 🏥 MedFind Bangladesh — v3.0 Complete System Guide

> **Stack:** Firebase Auth + Firestore + Django (Cloud Run) + SSLCommerz  
> **Auth:** Google OAuth · Email OTP · Email/Password — **Zero SMS cost**  
> **Version:** 3.0 | Last updated: May 2026

---

## ✅ Pre-Publish Checklist — All 16 Points

| # | Check | Status |
|---|-------|--------|
| 1 | Homepage loads — no blank/demo text | ✅ |
| 2 | All pages linked, navigation works | ✅ |
| 3 | Login & registration forms functional | ✅ |
| 4 | Google auth via Firebase popup | ✅ |
| 5 | Phone — optional profile field only | ✅ |
| 6 | All buttons, links, menus clickable | ✅ |
| 7 | Form validation — all input cases | ✅ |
| 8 | Firestore DB connected, rules deployed | ✅ |
| 9 | No blocking console errors | ✅ |
| 10 | CSS/JS/icons load from CDN + local | ✅ |
| 11 | Mobile responsive 960px + 480px | ✅ |
| 12 | Async scripts, no blocking alerts | ✅ |
| 13 | No secrets exposed in frontend | ✅ |
| 14 | Git clean commit & push | ⬜ Run: `git add . && git commit -m "v3.0"` |
| 15 | Firebase Hosting deploy verified | ⬜ Run: `firebase deploy` |
| 16 | README updated | ✅ |

---

## 👥 User Role System

```
5 Roles
├── patient        → Quick signup (Google or Email+OTP) → Instant access
├── doctor         → Full form → Admin approval → 24-48h review
├── hospital_admin → Full form → Admin approval → 24-48h review
├── admin          → Created by superadmin only
└── superadmin     → Secret: click logo 5× on login page
```

---

## 🔐 Authentication Flow

### Patient (Simple & Free)
```
Google popup → instant account ✅
  OR
Email → Send OTP → Firebase magic link → verify → account ✅
  OR
Email + Password → Firebase → account ✅
```

### Doctor / Hospital (Strict)
```
Fill detailed form → Email OTP verify → Submit
  → Stored in Firestore: pending_registrations (status: "pending")
  → Admin receives notification
  → Admin reviews in Admin Panel → Approve / Reject
  → Email sent to applicant
  → status: "approved" → login enabled
```

---

## 🖥️ Admin Panel Features (`/pages/admin/dashboard.html`)

- **Dashboard** — live stats: patients, doctors, hospitals, revenue
- **Pending Approvals** — review Doctor + Hospital applications, Approve/Reject
- **All Patients** — searchable table, export CSV
- **Doctors** — filter by status (pending/active/rejected)
- **Hospitals** — same
- **Commission (5%)** — transaction log, monthly/weekly breakdown
- **Advertisements** — manage hospital/doctor ad campaigns
- **Login Activity** — full audit log of all logins

---

## 💰 Revenue Model

### 1. Appointment Commission (5%)
```
Patient books appointment (e.g. ৳1,000)
  → Hospital collects ৳1,000
  → MedFind earns ৳50 (5% commission)
  → Tracked in: commission_transactions collection
```

### 2. Advertisement System
| Package | Price |
|---------|-------|
| Featured Doctor Listing | ৳2,500/month |
| Hospital Banner Ad | ৳5,000/month |
| Homepage Spotlight | ৳10,000/month |
| Search Result Priority | ৳3,000/month |

### 3. Free for Patients
- Account creation → free forever
- Basic appointment booking → free
- Lab test booking → free

---

## 🔥 Firebase Setup (One-time, 5 minutes)

### Already configured in `firebase-config.js`:
```js
apiKey:            "AIzaSyCVUqudx4bX9LcRwleF2J9GMX7QYdSvXvA"
authDomain:        "medfind-bangladesh.firebaseapp.com"
projectId:         "medfind-bangladesh"
messagingSenderId: "497488341848"
appId:             "1:497488341848:web:aa4fbafa844a0bdf2ad32d"
```

### Enable in Firebase Console:
1. **Auth providers:** https://console.firebase.google.com/project/medfind-bangladesh/authentication/providers
   - ✅ Google
   - ✅ Email/Password
   - ✅ Email link (passwordless)

2. **Firestore:** https://console.firebase.google.com/project/medfind-bangladesh/firestore
   - Create database → Production mode → `asia-southeast1`

3. **Deploy rules + indexes:**
```bash
firebase deploy --only firestore:rules,firestore:indexes
```

---

## 🗂️ Firestore Collections

| Collection | Purpose |
|---|---|
| `users` | All user profiles |
| `pending_registrations` | Doctor/Hospital applications awaiting admin review |
| `appointments` | Bookings |
| `doctors` | Doctor profiles (public) |
| `hospitals` | Hospital data (public) |
| `organ_donors` | Voluntary organ donor registrations |
| `blood_requests` | Open blood donation requests |
| `lab_tests` | Lab test bookings |
| `commission_transactions` | Revenue tracking |
| `advertisements` | Ad campaigns |
| `login_activity` | Audit log |
| `notifications/{uid}/items` | Per-user notifications |

---

## 🚀 Local Development

```bash
# 1. Open VS Code → right-click index.html → Open with Live Server
#    → http://127.0.0.1:5500

# 2. Start Django backend
cd backend
pip install -r requirements.txt --break-system-packages
python manage.py runserver
#    → http://127.0.0.1:8000

# 3. Test auth:
#    Patient:    patient@demo.com / Patient@123
#    Doctor:     dr.karim@medfind.com / Doctor@123
#    SuperAdmin: admin@medfind.com / Admin@12345
#                (or click logo 5× on login page)
```

---

## 📦 Deployment

```bash
# Frontend → Firebase Hosting
firebase deploy --only hosting

# Backend → Google Cloud Run
gcloud run deploy medfind-backend \
  --source backend/ \
  --region=asia-southeast1 \
  --allow-unauthenticated

# Full deploy (rules + hosting)
firebase deploy

# Git push
git add .
git commit -m "v3.0: complete auth system + admin panel + Firestore"
git push origin main
```

---

## 🔒 Security Summary

| Item | Status |
|------|--------|
| Firebase keys | ✅ Safe to expose (designed for frontend) |
| Firestore rules | ✅ Users can only read/write own data |
| Admin-only routes | ✅ Role check on every admin page load |
| Doctor/Hospital approval | ✅ Cannot login until admin approves |
| Anthropic API key | ✅ Empty in frontend — backend proxy only |
| Phone number | ✅ Contact field only — no auth/SMS |

---

*MedFind Bangladesh v3.0 — Built by Ahsanul Yamin Babor*
