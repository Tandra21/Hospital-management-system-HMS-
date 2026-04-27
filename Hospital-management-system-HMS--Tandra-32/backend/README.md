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
