# MEDFIND Backend Setup Guide - Complete

এই গাইড অনুসরণ করে আপনার Django ব্যাকএন্ড এবং MongoDB সেটআপ সম্পূর্ণ করুন।

## 🎯 দ্রুত শুরু (Quick Start) - 5 মিনিটে

### Step 1: MongoDB চালান

```bash
# Windows PowerShell এ
mongod

# অন্য terminal এ:
mongosh
```

### Step 2: Backend Setup

```bash
# Project root থেকে backend folder এ যান
cd backend

# Virtual Environment তৈরি করুন
python -m venv venv

# Activate করুন (Windows)
venv\Scripts\activate

# Dependencies ইনস্টল করুন
pip install -r requirements.txt
```

### Step 3: Django Server চালান

```bash
# Backend directory থেকে
python manage.py runserver
```

✅ হয়ে গেছে! Server চলছে: **http://localhost:8000**

---

## 📋 বিস্তারিত গাইড

### A. MongoDB সেটআপ (Windows)

#### 1. ডাউনলোড এবং ইনস্টলেশন

```
1. https://www.mongodb.com/try/download/community সাইটে যান
2. Windows 64-bit এ click করুন
3. Installer run করুন এবং default settings এ OK করুন
4. MongoDB সার্ভিস auto-install হবে
```

#### 2. MongoDB Server চালু করুন

**Option A: Service হিসেবে (Recommended)**
```
MongoDB পূর্বনির্ধারিতভাবে Windows Service হিসেবে চলবে
```

**Option B: Manual শুরু করুন**
```powershell
mongod
```

#### 3. MongoDB Shell খুলুন (অন্য terminal এ)
```powershell
mongosh
```

---

### B. Python Environment Setup

#### 1. Python ইনস্টল করুন (3.8 বা তার উপরে)

```powershell
# Check Python version
python --version
```

#### 2. Backend Directory Navigate করুন

```powershell
cd "path/to/Hospital-management-system-HMS-/backend"
```

#### 3. Virtual Environment তৈরি করুন

```powershell
# Create venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# আপনি দেখবেন prompt এ (venv) prefix
# Example: (venv) PS C:\path\to\backend>
```

#### 4. Requirements ইনস্টল করুন

```powershell
pip install -r requirements.txt
```

---

### C. Django Configuration

#### 1. Environment Variables সেটআপ করুন

`.env` ফাইল এ যোগ করুন:

```env
# Django
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here-change-this-in-production
ALLOWED_HOSTS=127.0.0.1,localhost

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DBNAME=medfind_db

# CORS
CORS_ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500
```

#### 2. Django Server চালু করুন

```powershell
python manage.py runserver
```

✅ Output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🔌 API Testing

### Browser এ টেস্ট করুন

```
http://localhost:8000/api/hospitals/
```

আপনি একটি JSON response পাবেন (এখন খালি array থাকবে)

### Thunder Client / Postman দিয়ে টেস্ট করুন

**GET Request:**
```
http://localhost:8000/api/hospitals/
```

**POST Request - হাসপাতাল তৈরি করুন:**
```
URL: http://localhost:8000/api/hospitals/
Method: POST
Body:
{
    "name": "City Hospital",
    "email": "info@cityhospital.com",
    "phone": "+1234567890",
    "address": {
        "street": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "postal_code": "10001"
    },
    "license_number": "LIC001",
    "specialties": ["Cardiology", "Neurology"],
    "bed_count": 100,
    "ambulance_available": true,
    "emergency_services": true,
    "is_active": true
}
```

---

## 📱 Frontend Integration

### 1. Portal Selection Page খোলুন

```
http://localhost:5500/basics/portal-selection.html
```

### 2. API Client ব্যবহার করুন

আপনার HTML এ add করুন:

```html
<script src="JSprogram/api-client.js"></script>

<script>
    // হাসপাতাল লিস্ট fetch করুন
    api.getHospitals().then(hospitals => {
        console.log('Hospitals:', hospitals);
    }).catch(error => {
        console.error('Error:', error);
    });

    // অ্যাপয়েন্টমেন্ট বুক করুন
    api.createAppointment({
        patient: 'patient_id_here',
        doctor: 'doctor_id_here',
        hospital: 'hospital_id_here',
        appointment_date: '2024-01-15T10:00:00',
        appointment_type: 'In-Person',
        reason_for_visit: 'General Checkup',
        status: 'Scheduled'
    }).then(appointment => {
        console.log('Appointment created:', appointment);
    }).catch(error => {
        console.error('Error:', error);
    });
</script>
```

---

## 🐛 সমস্যা সমাধান

### সমস্যা 1: MongoDB Connection Error

```
Error: [Errno 10061] Connect call failed
```

**সমাধান:**
```powershell
# MongoDB Server চলু আছে কিনা check করুন
mongosh

# যদি fail হয়, MongoDB install করুন:
# https://www.mongodb.com/try/download/community
```

### সমস্যা 2: Port Already in Use

```
Error: Address already in use
```

**সমাধান:**
```powershell
# অন্য port এ চালু করুন
python manage.py runserver 8001
```

### সমস্যা 3: ModuleNotFoundError

```
Error: No module named 'django'
```

**সমাধান:**
```powershell
# Virtual environment activate আছে কিনা check করুন
venv\Scripts\activate

# Requirements again install করুন
pip install -r requirements.txt
```

### সমস্যা 4: CORS Error

```javascript
Access to XMLHttpRequest blocked by CORS policy
```

**সমাধান:**
- `.env` এ `CORS_ALLOWED_ORIGINS` check করুন
- Frontend URL যোগ করুন (যেমন: `http://localhost:5500`)

---

## 📊 Database Management

### MongoDB Collections দেখুন

```powershell
mongosh

# Database select করুন
use medfind_db

# Collections দেখুন
show collections

# Documents দেখুন
db.hospitals.find()
```

### Data Clear করুন

```javascript
db.hospitals.deleteMany({})
db.doctors.deleteMany({})
db.patients.deleteMany({})
```

---

## 🚀 পরবর্তী ধাপ

1. **Frontend Integration:** Portal pages গুলি API কল করার জন্য update করুন
2. **Authentication:** User login/registration implement করুন
3. **File Upload:** Doctor profile images, medical reports upload করুন
4. **Real-time Updates:** WebSocket implement করুন appointment notifications এর জন্য
5. **Production Deploy:** Heroku/AWS এ deploy করুন

---

## 📚 ফাইল কাঠামো রেফারেন্স

```
backend/
├── manage.py                 # Django command-line tool
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore file
├── medfind_backend/
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI app
│   └── api/
│       ├── __init__.py
│       ├── models.py        # MongoDB Models
│       ├── views.py         # API ViewSets
│       ├── serializers.py   # Data serializers
│       ├── urls.py          # API URLs
│       ├── utils.py         # Helper functions
│       ├── admin.py         # Admin panel
│       ├── apps.py          # App config
│       ├── tests.py         # Unit tests
│       └── migrations/
└── README.md                # Backend documentation
```

---

## 🎓 সহায়ক লিঙ্ক

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [MongoEngine Documentation](https://mongoengine-odm.readthedocs.io/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

## 💡 টিপস

1. **Development এ Debug Mode On রাখুন**: `DEBUG=True` in `.env`
2. **Production এ Debug Off করুন**: `DEBUG=False`
3. **Logs check করুন**: Terminal output এ error messages দেখুন
4. **API Test করুন**: Thunder Client / Postman ব্যবহার করুন
5. **Database Backup করুন**: নিয়মিত data backup নিন

---

## ✅ Success Checklist

- [ ] MongoDB installed এবং running
- [ ] Python 3.8+ installed
- [ ] Virtual environment created এবং activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] Django server running (`python manage.py runserver`)
- [ ] API accessible (`http://localhost:8000/api/`)
- [ ] Frontend can communicate with backend

---

**Congratulations! 🎉 আপনার Hospital Management System Backend প্রস্তুত!**

যদি কোনো সমস্যা হয়, Backend README.md ফাইল পড়ুন বা documentation check করুন।

Happy Coding! 🚀
