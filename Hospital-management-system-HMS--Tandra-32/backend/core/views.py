from datetime import datetime
from bson.objectid import ObjectId
from django.shortcuts import render, redirect
from django.http import Http404
from .mongo_client import get_database

db = get_database()


def home(request):
    doctors = list(db.doctors.find({}, {'name': 1, 'specialty': 1}).limit(6))
    hospitals = list(db.hospitals.find({}, {'name': 1, 'city': 1}).limit(6))
    return render(request, 'core/home.html', {'doctors': doctors, 'hospitals': hospitals})


def doctor_search(request):
    query = request.GET.get('q', '').strip()
    mongo_query = {}
    if query:
        mongo_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'specialty': {'$regex': query, '$options': 'i'}},
                {'hospital': {'$regex': query, '$options': 'i'}},
            ]
        }
    doctors = list(db.doctors.find(mongo_query))
    hospitals = list(db.hospitals.find(mongo_query))
    return render(request, 'core/doctor_search.html', {'doctors': doctors, 'hospitals': hospitals, 'query': query})


def doctor_detail(request, doctor_id):
    try:
        doctor = db.doctors.find_one({'_id': ObjectId(doctor_id)})
    except Exception:
        raise Http404('Doctor not found')
    if not doctor:
        raise Http404('Doctor not found')
    return render(request, 'core/doctor_detail.html', {'doctor': doctor})


def hospital_detail(request, hospital_id):
    try:
        hospital = db.hospitals.find_one({'_id': ObjectId(hospital_id)})
    except Exception:
        raise Http404('Hospital not found')
    if not hospital:
        raise Http404('Hospital not found')
    doctors = list(db.doctors.find({'hospital': hospital['name']}))
    return render(request, 'core/hospital_detail.html', {'hospital': hospital, 'doctors': doctors})


def book_doctor(request, doctor_id):
    try:
        doctor = db.doctors.find_one({'_id': ObjectId(doctor_id)})
    except Exception:
        raise Http404('Doctor not found')
    if not doctor:
        raise Http404('Doctor not found')

    if request.method == 'POST':
        patient_name = request.POST.get('name', '').strip()
        patient_email = request.POST.get('email', '').strip()
        patient_phone = request.POST.get('phone', '').strip()
        appointment_date = request.POST.get('date', '').strip()

        if not patient_name or not patient_email or not appointment_date:
            return render(request, 'core/book_doctor.html', {
                'doctor': doctor,
                'error': 'Please provide name, email, and appointment date.',
            })

        db.bookings.insert_one({
            'doctor_id': doctor['_id'],
            'doctor_name': doctor['name'],
            'patient_name': patient_name,
            'patient_email': patient_email,
            'patient_phone': patient_phone,
            'appointment_date': appointment_date,
            'created_at': datetime.utcnow(),
        })
        return redirect('core:booking_success')

    return render(request, 'core/book_doctor.html', {'doctor': doctor})


def booking_success(request):
    return render(request, 'core/booking_success.html')
