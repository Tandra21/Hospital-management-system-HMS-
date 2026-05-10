# MEDFIND API - Quick Reference Guide

সবচেয়ে ব্যবহৃত API Endpoints

## 📌 Base URL
```
http://localhost:8000/api
```

---

## 🏥 Hospital Endpoints

### Get All Hospitals
```
GET /hospitals/
```
**Query Parameters:**
- `city` - City name (e.g., ?city=New York)
- `specialty` - Medical specialty (e.g., ?specialty=Cardiology)
- `search` - Search term

**Example:**
```javascript
api.getHospitals({ city: 'New York', specialty: 'Cardiology' })
```

### Get Hospital Details
```
GET /hospitals/{hospital_id}/
```

### Get Doctors in Hospital
```
GET /hospitals/{hospital_id}/doctors/
```

### Get Hospital Services
```
GET /hospitals/{hospital_id}/services/
```

### Create New Hospital
```
POST /hospitals/
Content-Type: application/json

{
    "name": "Hospital Name",
    "email": "info@hospital.com",
    "phone": "+1234567890",
    "address": {
        "street": "123 Main St",
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

## 👨‍⚕️ Doctor Endpoints

### Get All Doctors
```
GET /doctors/
```
**Query Parameters:**
- `specialization` - Doctor's specialty
- `hospital_id` - Filter by hospital
- `search` - Search by name

### Get Doctor Details
```
GET /doctors/{doctor_id}/
```

### Get Doctor Availability
```
GET /doctors/{doctor_id}/availability/
```

### Create New Doctor
```
POST /doctors/
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@hospital.com",
    "phone": "+1-555-1001",
    "specialization": "Cardiology",
    "qualifications": ["MD", "Board Certified"],
    "experience_years": 15,
    "hospital": "hospital_id",
    "consultation_fee": 150.0,
    "available_days": ["Monday", "Tuesday", "Wednesday"],
    "bio": "Expert cardiologist",
    "license_number": "MD-001",
    "is_active": true
}
```

---

## 👥 Patient Endpoints

### Get All Patients
```
GET /patients/
```

### Get Patient Details
```
GET /patients/{patient_id}/
```

### Get Patient Medical History
```
GET /patients/{patient_id}/medical_history/
```

### Get Patient Appointments
```
GET /patients/{patient_id}/appointments/
```

### Create New Patient
```
POST /patients/
Content-Type: application/json

{
    "first_name": "Robert",
    "last_name": "Brown",
    "email": "robert@email.com",
    "phone": "+1-555-2001",
    "gender": "Male",
    "blood_group": "O+",
    "date_of_birth": "1980-05-15T00:00:00",
    "address": {
        "street": "100 Patient St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "postal_code": "10002"
    },
    "emergency_contact": "Jane Brown",
    "emergency_contact_phone": "+1-555-2002",
    "medical_conditions": ["Hypertension"],
    "allergies": ["Penicillin"],
    "medications": ["Lisinopril"],
    "is_active": true
}
```

---

## 📅 Appointment Endpoints

### Get All Appointments
```
GET /appointments/
```

### Get Appointments by Patient
```
GET /appointments/by_patient/?patient_id={patient_id}
```

### Get Appointments by Doctor
```
GET /appointments/by_doctor/?doctor_id={doctor_id}
```

### Get Appointment Details
```
GET /appointments/{appointment_id}/
```

### Create Appointment
```
POST /appointments/
Content-Type: application/json

{
    "patient": "patient_id",
    "doctor": "doctor_id",
    "hospital": "hospital_id",
    "appointment_date": "2024-01-15T10:00:00",
    "appointment_type": "In-Person",
    "reason_for_visit": "Cardiac Checkup",
    "status": "Scheduled",
    "notes": "Follow-up appointment"
}
```

**Appointment Types:** In-Person, Online, Phone
**Statuses:** Scheduled, Completed, Cancelled, No-Show

### Update Appointment Status
```
PUT /appointments/{appointment_id}/
Content-Type: application/json

{
    "status": "Completed",
    "prescription": "Take prescribed medicine"
}
```

---

## 🧪 Lab Test Endpoints

### Get All Lab Tests
```
GET /lab-tests/
```

### Get Lab Tests by Patient
```
GET /lab-tests/by_patient/?patient_id={patient_id}
```

### Get Lab Test Details
```
GET /lab-tests/{test_id}/
```

### Create Lab Test
```
POST /lab-tests/
Content-Type: application/json

{
    "patient": "patient_id",
    "hospital": "hospital_id",
    "test_name": "Blood Test",
    "test_code": "BT-001",
    "category": "Blood",
    "cost": 50.0,
    "status": "Pending",
    "description": "Complete blood count"
}
```

---

## 💰 Billing Endpoints

### Get All Billings
```
GET /billing/
```

### Get Billings by Patient
```
GET /billing/by_patient/?patient_id={patient_id}
```

### Get Billing Details
```
GET /billing/{billing_id}/
```

### Create Billing/Invoice
```
POST /billing/
Content-Type: application/json

{
    "patient": "patient_id",
    "hospital": "hospital_id",
    "invoice_number": "INV-001",
    "services": [
        {"name": "Consultation", "cost": 100},
        {"name": "Lab Test", "cost": 50}
    ],
    "total_amount": 150.0,
    "discount": 0.0,
    "tax": 15.0,
    "payable_amount": 165.0,
    "payment_method": "Cash",
    "payment_status": "Pending",
    "description": "Doctor consultation and lab tests"
}
```

### Mark Billing as Paid
```
POST /billing/{billing_id}/mark_as_paid/
```

---

## 💊 Pharmacy Endpoints

### Get All Medicines
```
GET /pharmacy/
```

### Get Medicine Details
```
GET /pharmacy/{medicine_id}/
```

### Create Medicine Entry
```
POST /pharmacy/
Content-Type: application/json

{
    "medicine_name": "Aspirin 500mg",
    "medicine_code": "ASP-500",
    "form": "Tablet",
    "strength": "500mg",
    "quantity_in_stock": 500,
    "price": 5.0,
    "reorder_level": 100,
    "hospital": "hospital_id",
    "manufacturer": "Pharma Corp",
    "supplier_name": "MediSupply Co",
    "expiry_date": "2025-12-31T00:00:00",
    "is_active": true
}
```

---

## 🧬 Medical History Endpoints

### Get Medical History Records
```
GET /medical-history/
```

### Get Medical History Details
```
GET /medical-history/{record_id}/
```

### Create Medical History Record
```
POST /medical-history/
Content-Type: application/json

{
    "patient": "patient_id",
    "doctor": "doctor_id",
    "hospital": "hospital_id",
    "visit_type": "Follow-up",
    "symptoms": ["Fever", "Cough"],
    "diagnosis": "Common Cold",
    "prescription": "Rest and hydration",
    "notes": "Mild case",
    "vital_signs": {
        "blood_pressure": "120/80",
        "temperature": "98.6",
        "heart_rate": 72
    }
}
```

---

## 🔄 Common Response Format

### Success Response
```json
[
    {
        "_id": {"$oid": "507f1f77bcf86cd799439011"},
        "name": "City Hospital",
        "email": "info@cityhospital.com",
        "phone": "+1-555-0101",
        ...
    }
]
```

### Error Response
```json
{
    "error": "Hospital not found",
    "status": 404
}
```

---

## 🚀 JavaScript Usage Examples

### Using the API Client

```javascript
// Include the API client
<script src="JSprogram/api-client.js"></script>

// Get all hospitals
api.getHospitals().then(hospitals => {
    console.log(hospitals);
}).catch(error => {
    console.error('Error:', error);
});

// Get hospital with filter
api.getHospitals({ city: 'New York', specialty: 'Cardiology' })
    .then(hospitals => console.log(hospitals));

// Get single hospital
api.getHospital('hospital_id').then(hospital => {
    console.log(hospital);
});

// Get doctors in hospital
api.getHospitalDoctors('hospital_id').then(doctors => {
    console.log(doctors);
});

// Book appointment
api.createAppointment({
    patient: 'patient_id',
    doctor: 'doctor_id',
    hospital: 'hospital_id',
    appointment_date: new Date().toISOString(),
    appointment_type: 'In-Person',
    reason_for_visit: 'Check-up',
    status: 'Scheduled'
}).then(appointment => {
    console.log('Appointment booked:', appointment);
});

// Get patient appointments
api.getPatientAppointments('patient_id').then(appointments => {
    console.log(appointments);
});

// Create billing
api.createBilling({
    patient: 'patient_id',
    hospital: 'hospital_id',
    invoice_number: 'INV-' + Date.now(),
    services: [
        { name: 'Doctor Visit', cost: 100 }
    ],
    total_amount: 100,
    payable_amount: 115,
    payment_status: 'Pending'
}).then(billing => {
    console.log('Invoice created:', billing);
});

// Mark payment done
api.markBillingAsPaid('billing_id').then(result => {
    console.log('Payment marked as done');
});

// Test API connection
api.testConnection().then(result => {
    console.log(result);
});
```

---

## 🔑 Common Parameters

### Pagination
```
?page=1&page_size=10
```

### Filtering
```
?status=Scheduled
?payment_status=Paid
?city=New York
```

### Searching
```
?search=John
```

### Ordering
```
?ordering=created_at
?ordering=-created_at (descending)
```

---

## 📊 Status Values

**Appointment Status:**
- Scheduled
- Completed
- Cancelled
- No-Show

**Billing Status:**
- Pending
- Paid
- Failed
- Refunded

**Lab Test Status:**
- Pending
- Completed
- Cancelled

**Gender:**
- Male
- Female
- Other

**Blood Groups:**
- A+, A-, B+, B-, AB+, AB-, O+, O-

**Appointment Type:**
- In-Person
- Online
- Phone

**Medicine Form:**
- Tablet
- Capsule
- Liquid
- Injection
- Cream
- Other

---

## 🔗 Useful Links

- **Backend Documentation:** `/backend/README.md`
- **Setup Guide:** `/COMPLETE_BACKEND_SETUP.md`
- **API Client:** `/JSprogram/api-client.js`
- **Portal:** `/basics/portal-selection.html`

---

**Last Updated:** January 2024
**Version:** 1.0

Happy API Coding! 🚀
