from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['hospital_db']

def seed():
    db.doctors.delete_many({})
    db.hospitals.delete_many({})
    db.bookings.delete_many({})

    hospitals = [
        {
            'name': 'Dhaka Central Hospital',
            'city': 'Dhaka',
            'division': 'Dhaka',
            'phone': '+8801711000001',
            'rating': 4.8,
        },
        {
            'name': 'Chittagong Care Clinic',
            'city': 'Chittagong',
            'division': 'Chittagong',
            'phone': '+8801711000002',
            'rating': 4.6,
        },
    ]
    doctor_list = [
        {
            'name': 'Dr. Ayesha Rahman',
            'specialty': 'Cardiology',
            'qualification': 'MBBS, FCPS',
            'hospital': 'Dhaka Central Hospital',
            'location': 'Gulshan, Dhaka',
            'fee': 1200,
        },
        {
            'name': 'Dr. Imtiaz Kabir',
            'specialty': 'Neurology',
            'qualification': 'MBBS, FCPS',
            'hospital': 'Dhaka Central Hospital',
            'location': 'Dhanmondi, Dhaka',
            'fee': 1500,
        },
        {
            'name': 'Dr. Sohana Akter',
            'specialty': 'Pediatrics',
            'qualification': 'MBBS, MD',
            'hospital': 'Chittagong Care Clinic',
            'location': 'Chittagong City',
            'fee': 900,
        },
    ]

    db.hospitals.insert_many(hospitals)
    db.doctors.insert_many(doctor_list)

    print('Seed data inserted:')
    print(f'  hospitals={db.hospitals.count_documents({})}')
    print(f'  doctors={db.doctors.count_documents({})}')
    print('MongoDB hospital_db is ready to use.')

if __name__ == '__main__':
    seed()
