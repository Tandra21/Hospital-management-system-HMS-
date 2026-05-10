from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['hospital_db']

def seed():
    db.doctors.delete_many({})
    db.hospitals.delete_many({})
    db.bookings.delete_many({})
    db.appointments.delete_many({})
    db.medicines.delete_many({})
    db.medicine_orders.delete_many({})

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
        {
            'name': 'Rajshahi Medical Center',
            'city': 'Rajshahi',
            'division': 'Rajshahi',
            'phone': '+8801711000003',
            'rating': 4.7,
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
        {
            'name': 'Dr. Rafiqul Islam',
            'specialty': 'Orthopedics',
            'qualification': 'MBBS, MS',
            'hospital': 'Rajshahi Medical Center',
            'location': 'Rajshahi City',
            'fee': 1100,
        },
        {
            'name': 'Dr. Nusrat Jahan',
            'specialty': 'Dermatology',
            'qualification': 'MBBS, DD',
            'hospital': 'Dhaka Central Hospital',
            'location': 'Banani, Dhaka',
            'fee': 1000,
        },
        {
            'name': 'Dr. Kamal Hossain',
            'specialty': 'General Medicine',
            'qualification': 'MBBS, MD',
            'hospital': 'Chittagong Care Clinic',
            'location': 'Chittagong City',
            'fee': 800,
        },
    ]

    db.hospitals.insert_many(hospitals)
    db.doctors.insert_many(doctor_list)

    medicines = [
        {
            'name': 'Napa Extra',
            'generic': 'Paracetamol + Caffeine',
            'category': 'Pain Relief',
            'icon': '💊',
            'price': 15,
            'unit': 'strip',
            'stock': 'In Stock',
            'description': 'মাথাব্যথা, জ্বর ও ব্যথায় দ্রুত উপশম।',
            'dosage': '১-২ ট্যাবলেট ৪-৬ ঘন্টা পর পর।',
            'warnings': 'কিডনি রোগীরা সতর্ক থাকবেন। অ্যালকোহলের সাথে ব্যবহার এড়িয়ে চলুন।',
            'sideEffects': ['বমি', 'মাথা ঘোরা', 'অনিদ্রা'],
        },
        {
            'name': 'Seclo 20',
            'generic': 'Omeprazole',
            'category': 'Antacid',
            'icon': '🧪',
            'price': 80,
            'unit': 'strip',
            'stock': 'In Stock',
            'description': 'গ্যাস্ট্রিক ও বুকজ্বালা উপশমে ব্যবহৃত।',
            'dosage': 'দিনে একবার, খাবারের আগে।',
            'warnings': 'দীর্ঘমেয়াদে হাড়ের ঘনত্ব কমতে পারে।',
            'sideEffects': ['মাথা ব্যথা', 'ডায়রিয়া', 'পেট ফাঁপা'],
        },
        {
            'name': 'Amoxicillin 500',
            'generic': 'Amoxicillin Trihydrate',
            'category': 'Antibiotic',
            'icon': '💉',
            'price': 120,
            'unit': 'strip',
            'stock': 'In Stock',
            'description': 'ব্যাকটেরিয়াল ইনফেকশন চিকিৎসায় ব্যবহৃত এন্টিবায়োটিক।',
            'dosage': '৫০০mg দিনে ৩ বার, ৫-৭ দিন।',
            'warnings': 'পেনিসিলিন এলার্জি থাকলে ব্যবহার করবেন না।',
            'sideEffects': ['ডায়রিয়া', 'বমি', 'র‍্যাশ'],
        },
        {
            'name': 'Metformin 500',
            'generic': 'Metformin HCl',
            'category': 'Antidiabetic',
            'icon': '🩺',
            'price': 50,
            'unit': 'strip',
            'stock': 'Low Stock',
            'description': 'টাইপ ২ ডায়াবেটিস নিয়ন্ত্রণে ব্যবহৃত।',
            'dosage': '৫০০mg দিনে ২ বার, খাবারের সাথে।',
            'warnings': 'কিডনি রোগে সতর্কতার সাথে ব্যবহার।',
            'sideEffects': ['বমি', 'পেটে অস্বস্তি', 'ক্ষুধামন্দা'],
        },
        {
            'name': 'Cetirizine 10',
            'generic': 'Cetirizine HCl',
            'category': 'Antihistamine',
            'icon': '🌿',
            'price': 35,
            'unit': 'strip',
            'stock': 'In Stock',
            'description': 'অ্যালার্জি ও হাঁচির জন্য দ্রুত কার্যকর ওষুধ।',
            'dosage': 'দিনে একবার রাতে।',
            'warnings': 'গাড়ি চালানোর আগে সতর্ক থাকুন।',
            'sideEffects': ['ঘুমঘুম ভাব', 'মুখ শুকানো', 'মাথা ব্যথা'],
        },
        {
            'name': 'Amlodipine 5',
            'generic': 'Amlodipine Besylate',
            'category': 'Antihypertensive',
            'icon': '❤️',
            'price': 60,
            'unit': 'strip',
            'stock': 'In Stock',
            'description': 'উচ্চ রক্তচাপ নিয়ন্ত্রণে ব্যবহৃত।',
            'dosage': '৫mg দিনে একবার।',
            'warnings': 'হঠাৎ বন্ধ করবেন না। গর্ভাবস্থায় ব্যবহার ডাক্তারের পরামর্শে।',
            'sideEffects': ['পা ফোলা', 'মাথা ঘোরা', 'মুখ লাল হওয়া'],
        },
        {
            'name': 'Fluconazole 150',
            'generic': 'Fluconazole',
            'category': 'Antifungal',
            'icon': '🍄',
            'price': 90,
            'unit': 'capsule',
            'stock': 'In Stock',
            'description': 'ফাঙ্গাল ইনফেকশনের চিকিৎসায় ব্যবহৃত।',
            'dosage': '১৫০mg একবার।',
            'warnings': 'লিভার সমস্যায় সতর্কতার সাথে ব্যবহার।',
            'sideEffects': ['মাথা ব্যথা', 'বমি', 'পেট ব্যথা'],
        },
        {
            'name': 'Vitamin D3 1000IU',
            'generic': 'Cholecalciferol',
            'category': 'Vitamin',
            'icon': '☀️',
            'price': 250,
            'unit': 'bottle',
            'stock': 'In Stock',
            'description': 'হাড় ও ইমিউন সিস্টেম শক্তিশালী করে।',
            'dosage': 'দিনে একবার খাবারের সাথে।',
            'warnings': 'অতিরিক্ত ডোজে ক্যালসিয়াম বাড়তে পারে।',
            'sideEffects': ['বমি', 'ক্লান্তি'],
        },
    ]
    db.medicines.insert_many(medicines)

    print('Seed data inserted:')
    print(f'  hospitals={db.hospitals.count_documents({})}')
    print(f'  doctors={db.doctors.count_documents({})}')
    print(f'  medicines={db.medicines.count_documents({})}')
    print('MongoDB hospital_db is ready to use.')

if __name__ == '__main__':
    seed()
