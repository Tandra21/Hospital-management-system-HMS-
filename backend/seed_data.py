"""
Sample data seeding script for MEDFIND
Run this script to populate MongoDB with sample data
Usage: python seed_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medfind_backend.settings')
django.setup()

from api.models import (
    Hospital, Doctor, Patient, Appointment, LabTest,
    Billing, Pharmacy, MedicalHistory, Address, WorkingHours
)


def clear_collections():
    """Clear all collections"""
    print("🗑️  Clearing existing data...")
    Hospital.drop_collection()
    Doctor.drop_collection()
    Patient.drop_collection()
    Appointment.drop_collection()
    LabTest.drop_collection()
    Billing.drop_collection()
    Pharmacy.drop_collection()
    MedicalHistory.drop_collection()
    print("✅ Collections cleared")


def create_hospitals():
    """Create sample hospitals"""
    print("\n🏥 Creating hospitals...")
    
    hospitals_data = [
        {
            'name': 'City Central Hospital',
            'email': 'info@citycentral.com',
            'phone': '+1-555-0101',
            'description': 'Leading healthcare provider in the city',
            'address': Address(
                street='123 Medical Avenue',
                city='New York',
                state='NY',
                country='USA',
                postal_code='10001',
                latitude=40.7128,
                longitude=-74.0060
            ),
            'logo': 'https://via.placeholder.com/200',
            'website': 'https://citycentral.com',
            'license_number': 'NYC-HOSP-001',
            'specialties': ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics'],
            'bed_count': 500,
            'ambulance_available': True,
            'emergency_services': True,
            'is_active': True,
        },
        {
            'name': 'Sunrise Medical Complex',
            'email': 'contact@sunrise.com',
            'phone': '+1-555-0102',
            'description': 'Specialized medical center for advanced treatments',
            'address': Address(
                street='456 Health Street',
                city='Los Angeles',
                state='CA',
                country='USA',
                postal_code='90001',
                latitude=34.0522,
                longitude=-118.2437
            ),
            'logo': 'https://via.placeholder.com/200',
            'website': 'https://sunrise.com',
            'license_number': 'LAX-HOSP-001',
            'specialties': ['Oncology', 'Cardiology', 'Surgery', 'Internal Medicine'],
            'bed_count': 300,
            'ambulance_available': True,
            'emergency_services': True,
            'is_active': True,
        },
        {
            'name': 'Green Valley Hospital',
            'email': 'admin@greenvalley.com',
            'phone': '+1-555-0103',
            'description': 'Community healthcare facility with modern equipment',
            'address': Address(
                street='789 Wellness Road',
                city='Chicago',
                state='IL',
                country='USA',
                postal_code='60601',
                latitude=41.8781,
                longitude=-87.6298
            ),
            'logo': 'https://via.placeholder.com/200',
            'website': 'https://greenvalley.com',
            'license_number': 'CHI-HOSP-001',
            'specialties': ['General Practice', 'Pediatrics', 'Gynecology', 'Orthopedics'],
            'bed_count': 200,
            'ambulance_available': True,
            'emergency_services': True,
            'is_active': True,
        }
    ]

    hospitals = []
    for data in hospitals_data:
        hospital = Hospital(**data)
        hospital.save()
        hospitals.append(hospital)
        print(f"  ✅ Created: {hospital.name}")
    
    return hospitals


def create_doctors(hospitals):
    """Create sample doctors"""
    print("\n👨‍⚕️  Creating doctors...")
    
    doctors_data = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@hospital.com',
            'phone': '+1-555-1001',
            'specialization': 'Cardiology',
            'qualifications': ['MD', 'Board Certified Cardiologist'],
            'experience_years': 15,
            'hospital': hospitals[0],
            'consultation_fee': 150.0,
            'available_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'bio': 'Expert cardiologist with 15 years of experience',
            'profile_image': 'https://via.placeholder.com/150',
            'license_number': 'MD-CAR-001',
            'is_active': True,
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@hospital.com',
            'phone': '+1-555-1002',
            'specialization': 'Neurology',
            'qualifications': ['MD', 'Neurology Specialist'],
            'experience_years': 10,
            'hospital': hospitals[0],
            'consultation_fee': 120.0,
            'available_days': ['Monday', 'Wednesday', 'Friday'],
            'bio': 'Specialized in neurological disorders',
            'profile_image': 'https://via.placeholder.com/150',
            'license_number': 'MD-NEU-001',
            'is_active': True,
        },
        {
            'first_name': 'Michael',
            'last_name': 'Williams',
            'email': 'michael.williams@hospital.com',
            'phone': '+1-555-1003',
            'specialization': 'Orthopedics',
            'qualifications': ['MD', 'Orthopedic Surgeon'],
            'experience_years': 12,
            'hospital': hospitals[1],
            'consultation_fee': 130.0,
            'available_days': ['Tuesday', 'Thursday', 'Friday'],
            'bio': 'Expert orthopedic surgeon',
            'profile_image': 'https://via.placeholder.com/150',
            'license_number': 'MD-ORT-001',
            'is_active': True,
        },
        {
            'first_name': 'Emma',
            'last_name': 'Davis',
            'email': 'emma.davis@hospital.com',
            'phone': '+1-555-1004',
            'specialization': 'Pediatrics',
            'qualifications': ['MD', 'Pediatrician'],
            'experience_years': 8,
            'hospital': hospitals[1],
            'consultation_fee': 100.0,
            'available_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
            'bio': 'Pediatric specialist focused on child health',
            'profile_image': 'https://via.placeholder.com/150',
            'license_number': 'MD-PED-001',
            'is_active': True,
        }
    ]

    doctors = []
    for data in doctors_data:
        doctor = Doctor(**data)
        doctor.save()
        doctors.append(doctor)
        print(f"  ✅ Created: Dr. {doctor.first_name} {doctor.last_name}")
    
    return doctors


def create_patients():
    """Create sample patients"""
    print("\n👥 Creating patients...")
    
    patients_data = [
        {
            'first_name': 'Robert',
            'last_name': 'Brown',
            'email': 'robert.brown@email.com',
            'phone': '+1-555-2001',
            'date_of_birth': datetime(1980, 5, 15),
            'gender': 'Male',
            'blood_group': 'O+',
            'address': Address(
                street='100 Patient Street',
                city='New York',
                state='NY',
                country='USA',
                postal_code='10002'
            ),
            'emergency_contact': 'Jane Brown',
            'emergency_contact_phone': '+1-555-2002',
            'medical_conditions': ['Hypertension', 'Diabetes'],
            'allergies': ['Penicillin'],
            'medications': ['Lisinopril', 'Metformin'],
            'is_active': True,
        },
        {
            'first_name': 'Lisa',
            'last_name': 'Anderson',
            'email': 'lisa.anderson@email.com',
            'phone': '+1-555-2003',
            'date_of_birth': datetime(1990, 8, 20),
            'gender': 'Female',
            'blood_group': 'A+',
            'address': Address(
                street='200 Health Avenue',
                city='New York',
                state='NY',
                country='USA',
                postal_code='10003'
            ),
            'emergency_contact': 'Mark Anderson',
            'emergency_contact_phone': '+1-555-2004',
            'medical_conditions': ['Asthma'],
            'allergies': ['Latex'],
            'medications': ['Albuterol'],
            'is_active': True,
        },
        {
            'first_name': 'David',
            'last_name': 'Martinez',
            'email': 'david.martinez@email.com',
            'phone': '+1-555-2005',
            'date_of_birth': datetime(1975, 3, 10),
            'gender': 'Male',
            'blood_group': 'B+',
            'address': Address(
                street='300 Wellness Road',
                city='Los Angeles',
                state='CA',
                country='USA',
                postal_code='90002'
            ),
            'emergency_contact': 'Maria Martinez',
            'emergency_contact_phone': '+1-555-2006',
            'medical_conditions': ['Heart Disease'],
            'allergies': ['Aspirin'],
            'medications': ['Atorvastatin', 'Carvedilol'],
            'is_active': True,
        }
    ]

    patients = []
    for data in patients_data:
        patient = Patient(**data)
        patient.save()
        patients.append(patient)
        print(f"  ✅ Created: {patient.first_name} {patient.last_name}")
    
    return patients


def create_appointments(patients, doctors, hospitals):
    """Create sample appointments"""
    print("\n📅 Creating appointments...")
    
    appointments_data = [
        {
            'patient': patients[0],
            'doctor': doctors[0],
            'hospital': hospitals[0],
            'appointment_date': datetime.now() + timedelta(days=5),
            'appointment_type': 'In-Person',
            'reason_for_visit': 'Cardiac Checkup',
            'status': 'Scheduled',
            'notes': 'Regular follow-up for heart condition',
        },
        {
            'patient': patients[1],
            'doctor': doctors[3],
            'hospital': hospitals[1],
            'appointment_date': datetime.now() + timedelta(days=3),
            'appointment_type': 'In-Person',
            'reason_for_visit': 'Pediatric Checkup',
            'status': 'Scheduled',
            'notes': 'Annual pediatric examination',
        },
        {
            'patient': patients[2],
            'doctor': doctors[0],
            'hospital': hospitals[0],
            'appointment_date': datetime.now() + timedelta(days=7),
            'appointment_type': 'Online',
            'reason_for_visit': 'Heart Disease Follow-up',
            'status': 'Scheduled',
            'notes': 'Online consultation for ongoing treatment',
        }
    ]

    appointments = []
    for data in appointments_data:
        appointment = Appointment(**data)
        appointment.save()
        appointments.append(appointment)
        print(f"  ✅ Created appointment for {appointment.patient.first_name}")
    
    return appointments


def create_pharmacy_items(hospitals):
    """Create sample pharmacy items"""
    print("\n💊 Creating pharmacy items...")
    
    pharmacy_data = [
        {
            'medicine_name': 'Aspirin 500mg',
            'medicine_code': 'ASP-500',
            'description': 'Pain reliever and fever reducer',
            'generic_name': 'Acetylsalicylic acid',
            'strength': '500mg',
            'form': 'Tablet',
            'quantity_in_stock': 500,
            'reorder_level': 100,
            'price': 5.0,
            'supplier_name': 'MediSupply Co',
            'manufacturer': 'Pharma Corp',
            'batch_number': 'BATCH-001',
            'expiry_date': datetime.now() + timedelta(days=365),
            'hospital': hospitals[0],
            'is_active': True,
        },
        {
            'medicine_name': 'Amoxicillin 250mg',
            'medicine_code': 'AMX-250',
            'description': 'Antibiotic for bacterial infections',
            'generic_name': 'Amoxicillin',
            'strength': '250mg',
            'form': 'Capsule',
            'quantity_in_stock': 300,
            'reorder_level': 100,
            'price': 3.50,
            'supplier_name': 'MediSupply Co',
            'manufacturer': 'Pharma Corp',
            'batch_number': 'BATCH-002',
            'expiry_date': datetime.now() + timedelta(days=365),
            'hospital': hospitals[1],
            'is_active': True,
        },
        {
            'medicine_name': 'Lisinopril 10mg',
            'medicine_code': 'LIS-10',
            'description': 'Blood pressure medication',
            'generic_name': 'Lisinopril',
            'strength': '10mg',
            'form': 'Tablet',
            'quantity_in_stock': 400,
            'reorder_level': 150,
            'price': 2.50,
            'supplier_name': 'MediSupply Co',
            'manufacturer': 'Pharma Corp',
            'batch_number': 'BATCH-003',
            'expiry_date': datetime.now() + timedelta(days=365),
            'hospital': hospitals[0],
            'is_active': True,
        }
    ]

    pharmacy_items = []
    for data in pharmacy_data:
        item = Pharmacy(**data)
        item.save()
        pharmacy_items.append(item)
        print(f"  ✅ Created: {item.medicine_name}")
    
    return pharmacy_items


def main():
    """Main seeding function"""
    print("=" * 50)
    print("🌱 MEDFIND Database Seeding Started")
    print("=" * 50)
    
    try:
        # Clear existing data
        clear_collections()
        
        # Create data
        hospitals = create_hospitals()
        doctors = create_doctors(hospitals)
        patients = create_patients()
        appointments = create_appointments(patients, doctors, hospitals)
        pharmacy = create_pharmacy_items(hospitals)
        
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print("=" * 50)
        print(f"""
📊 Summary:
  🏥 Hospitals: {len(hospitals)}
  👨‍⚕️  Doctors: {len(doctors)}
  👥 Patients: {len(patients)}
  📅 Appointments: {len(appointments)}
  💊 Medicines: {len(pharmacy)}

🚀 Next Steps:
  1. Start MongoDB: mongod
  2. Start Django: python manage.py runserver
  3. Visit: http://localhost:8000/api/hospitals/
  4. Try Portal: http://localhost:5500/basics/portal-selection.html
        """)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
