from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('doctor-search/', views.doctor_search, name='doctor_search'),
    path('doctor/<str:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctor/<str:doctor_id>/book/', views.book_doctor, name='book_doctor'),
    path('hospital/<str:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('booking/success/', views.booking_success, name='booking_success'),
]
