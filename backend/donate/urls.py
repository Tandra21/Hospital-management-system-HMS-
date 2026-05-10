# donate/urls.py
from django.urls import path
from .views import (DonorRegisterView, DonorLookupView,
                    DonorWithdrawView, DonorStatsView, BloodDonorSearchView)

urlpatterns = [
    path('register/',     DonorRegisterView.as_view(),     name='donate-register'),
    path('lookup/',       DonorLookupView.as_view(),       name='donate-lookup'),
    path('withdraw/',     DonorWithdrawView.as_view(),     name='donate-withdraw'),
    path('stats/',        DonorStatsView.as_view(),        name='donate-stats'),
    path('blood-search/', BloodDonorSearchView.as_view(),  name='donate-blood-search'),
]
