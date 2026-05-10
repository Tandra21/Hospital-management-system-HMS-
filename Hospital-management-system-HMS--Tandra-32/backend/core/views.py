from datetime import datetime
from bson.objectid import ObjectId
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .mongo_client import get_database
import json

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


def medicine_inventory(request):
    return render(request, 'core/medicine_inventory.html')


# API Views
@csrf_exempt
@require_http_methods(["GET"])
def api_doctors(request):
    doctors = []
    for doctor in db.doctors.find({}, {'name': 1, 'specialty': 1, 'fee': 1}):
        doctor['_id'] = str(doctor['_id'])
        doctors.append(doctor)
    return JsonResponse(doctors, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_appointment_book(request):
    try:
        data = request.POST
        
        required_fields = ['patient_name', 'patient_email', 'patient_phone', 'patient_dob', 
                          'doctor_id', 'appointment_date', 'appointment_time', 'appointment_type', 'symptoms']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Validate doctor exists
        try:
            doctor = db.doctors.find_one({'_id': ObjectId(data['doctor_id'])})
            if not doctor:
                return JsonResponse({'error': 'Doctor not found'}, status=404)
        except:
            return JsonResponse({'error': 'Invalid doctor ID'}, status=400)
        
        appointment = {
            'patient_name': data['patient_name'],
            'patient_email': data['patient_email'],
            'patient_phone': data['patient_phone'],
            'patient_dob': data['patient_dob'],
            'doctor_id': ObjectId(data['doctor_id']),
            'doctor_name': doctor['name'],
            'appointment_date': data['appointment_date'],
            'appointment_time': data['appointment_time'],
            'appointment_type': data['appointment_type'],
            'symptoms': data['symptoms'],
            'medical_history': data.get('medical_history', ''),
            'status': 'pending',
            'created_at': datetime.utcnow(),
        }
        
        result = db.appointments.insert_one(appointment)
        appointment['_id'] = str(result.inserted_id)
        
        return JsonResponse({'message': 'Appointment booked successfully', 'appointment_id': appointment['_id']})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_medicines(request):
    medicines = []
    for medicine in db.medicines.find({}):
        medicine['_id'] = str(medicine['_id'])
        medicines.append(medicine)
    return JsonResponse(medicines, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_medicine_order(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    if 'items' not in data or not isinstance(data['items'], list) or not data['items']:
        return JsonResponse({'error': 'Order items are required'}, status=400)

    if 'total_amount' not in data:
        return JsonResponse({'error': 'Total amount is required'}, status=400)

    try:
        total_amount = float(data['total_amount'])
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid total amount'}, status=400)

    order = {
        'items': data['items'],
        'total_amount': total_amount,
        'status': 'pending',
        'created_at': datetime.utcnow(),
    }
    if 'customer_name' in data:
        order['customer_name'] = data['customer_name']
    if 'customer_contact' in data:
        order['customer_contact'] = data['customer_contact']

    result = db.medicine_orders.insert_one(order)
    return JsonResponse({'message': 'Medicine order placed successfully', 'order_id': str(result.inserted_id)})
