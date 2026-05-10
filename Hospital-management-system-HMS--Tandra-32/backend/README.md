# Hospital Management Django Backend

This backend is a simple Django app that uses MongoDB for doctor, hospital, and booking data.

## Setup

1. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start MongoDB locally.
   - The app expects MongoDB at `mongodb://localhost:27017`.

3. Seed sample data:
   ```bash
   python seed_data.py
   ```

4. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

5. Open:
   - `http://127.0.0.1:8000/`
   - `http://127.0.0.1:8000/doctor-search/`

## Endpoints

- `/` — Home page
- `/doctor-search/` — Search doctors and hospitals
- `/doctor/<id>/` — Doctor detail page
- `/doctor/<id>/book/` — Booking page
- `/hospital/<id>/` — Hospital detail page
- `/booking/success/` — Booking confirmation

## API Endpoints

- `GET /api/doctors/` — Get list of all doctors (JSON)
- `POST /api/appointment-book/` — Book an appointment (form data)
- `GET /api/medicines/` — Get medicine inventory (JSON)
- `POST /api/medicine-order/` — Place a medicine order (JSON)

### Appointment Booking API

POST to `/api/appointment-book/` with form data:

- `patient_name` (required)
- `patient_email` (required)
- `patient_phone` (required)
- `patient_dob` (required)
- `doctor_id` (required)
- `appointment_date` (required)
- `appointment_time` (required)
- `appointment_type` (required)
- `symptoms` (required)
- `medical_history` (optional)

Returns JSON: `{"message": "Appointment booked successfully", "appointment_id": "..."}`

### Medicine Inventory API

GET `/api/medicines/` returns the current medicine inventory as JSON.

POST `/api/medicine-order/` with JSON body:

- `items` — array of objects with `id`, `name`, `price`, and `qty`
- `total_amount` — total order amount
- `customer_name` — optional
- `customer_contact` — optional

Returns JSON: `{"message": "Medicine order placed successfully", "order_id": "..."}`

