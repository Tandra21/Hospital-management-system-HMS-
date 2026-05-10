"""
MedFind Bangladesh — SSLCommerz Payment Gateway Backend
=====================================================
Super Admin: Ahsanul Yamin Barun
bKash/Nagad: 01772172829
Commission:  5% → Super Admin | 95% → Hospital Admin

Setup:
  pip install sslcommerz-python
  
Add to settings.py:
  SSLCOMMERZ_STORE_ID = 'your_store_id'
  SSLCOMMERZ_STORE_PASSWD = 'your_store_passwd'
  SSLCOMMERZ_IS_LIVE = False  # True in production
  
  SUPER_ADMIN_COMMISSION_PCT = 5
  SUPER_ADMIN_BKASH = '01772172829'
  SUPER_ADMIN_NAGAD = '01772172829'
"""

import hashlib
import uuid
import requests
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

User = get_user_model()

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
SUPER_ADMIN_PCT   = Decimal('5')    # 5% commission to Super Admin
HOSPITAL_PCT      = Decimal('95')   # 95% payout to Hospital Admin
SUPER_ADMIN_BKASH = '01772172829'   # Ahsanul Yamin Barun — bKash & Nagad
SUPER_ADMIN_NAGAD = '01772172829'

SSL_BASE_SANDBOX = 'https://sandbox.sslcommerz.com'
SSL_BASE_LIVE    = 'https://securepay.sslcommerz.com'


def get_ssl_base():
    return SSL_BASE_LIVE if getattr(settings, 'SSLCOMMERZ_IS_LIVE', False) else SSL_BASE_SANDBOX


def calculate_commission(amount: Decimal):
    """Split amount: 5% Super Admin, 95% Hospital"""
    commission = (amount * SUPER_ADMIN_PCT / 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
    hospital_payout = (amount - commission).quantize(Decimal('0.01'), ROUND_HALF_UP)
    return commission, hospital_payout


# ── INITIATE PAYMENT ──────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    POST /api/v1/payments/initiate/
    Body: {
        amount, booking_type, patient_name, patient_email, patient_phone,
        hospital_name, hospital_admin_id, booking_ref, booking_id
    }
    Returns: { status, GatewayPageURL, tran_id }
    """
    data = request.data
    amount = Decimal(str(data.get('total_amount') or data.get('amount', 0)))

    if amount <= 0:
        return Response({'status': 'FAILED', 'message': 'Invalid amount'}, status=400)

    commission, hospital_payout = calculate_commission(amount)
    tran_id = f"MF-{data.get('product_category', 'PAY').upper()}-{uuid.uuid4().hex[:10].upper()}"

    # Build SSLCommerz payload
    ssl_payload = {
        'store_id':         getattr(settings, 'SSLCOMMERZ_STORE_ID', 'testbox'),
        'store_passwd':     getattr(settings, 'SSLCOMMERZ_STORE_PASSWD', 'qwerty'),
        'total_amount':     str(amount),
        'currency':         'BDT',
        'tran_id':          tran_id,
        'success_url':      data.get('success_url', f'{request.scheme}://{request.get_host()}/payment/success/'),
        'fail_url':         data.get('fail_url',    f'{request.scheme}://{request.get_host()}/payment/fail/'),
        'cancel_url':       data.get('cancel_url',  f'{request.scheme}://{request.get_host()}/payment/cancel/'),
        'ipn_url':          f'{request.scheme}://{request.get_host()}/api/v1/payments/ipn/',

        # Customer
        'cus_name':         data.get('cus_name', 'MedFind Patient'),
        'cus_email':        data.get('cus_email', 'patient@medfind.com'),
        'cus_add1':         data.get('cus_add1', 'Bangladesh'),
        'cus_city':         'Dhaka',
        'cus_country':      'Bangladesh',
        'cus_phone':        data.get('cus_phone', '01700000000'),

        # Product
        'product_name':     data.get('product_name', 'MedFind Booking'),
        'product_category': data.get('product_category', 'healthcare'),
        'product_profile':  'general',

        # Commission metadata
        'value_a':  str(commission),           # Super Admin commission
        'value_b':  str(hospital_payout),      # Hospital payout
        'value_c':  str(data.get('value_c', '')),  # Hospital admin ID
        'value_d':  str(data.get('value_d', tran_id)),  # Booking reference
    }

    try:
        resp = requests.post(
            f"{get_ssl_base()}/gwprocess/apiV4/api.php",
            data=ssl_payload,
            timeout=30,
        )
        result = resp.json()

        if result.get('status') == 'SUCCESS':
            # Save pending payment record
            try:
                from apps.monetization.models import Payment, CommissionRecord
                payment = Payment.objects.create(
                    tran_id=tran_id,
                    amount=amount,
                    status='pending',
                    patient=request.user,
                    booking_type=data.get('product_category', 'appointment'),
                    commission_amount=commission,
                    hospital_payout=hospital_payout,
                    gateway_url=result.get('GatewayPageURL', ''),
                )
            except Exception:
                pass  # Models may not exist yet

            return Response({
                'status': 'SUCCESS',
                'GatewayPageURL': result.get('GatewayPageURL'),
                'tran_id': tran_id,
                'commission': str(commission),
                'hospital_payout': str(hospital_payout),
            })
        else:
            return Response({'status': 'FAILED', 'message': result.get('failedreason', 'SSLCommerz error')}, status=400)

    except requests.RequestException as e:
        return Response({'status': 'ERROR', 'message': f'Gateway unreachable: {str(e)}'}, status=503)


# ── IPN (Instant Payment Notification) ────────────────────────────────────────
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_ipn(request):
    """
    POST /api/v1/payments/ipn/
    SSLCommerz calls this after payment completes.
    Handles commission split: 5% Super Admin, 95% Hospital Admin.
    """
    data = request.data
    tran_id   = data.get('tran_id', '')
    status    = data.get('status', '')
    amount    = Decimal(str(data.get('amount', 0)))
    val_id    = data.get('val_id', '')

    # Verify payment with SSLCommerz
    verified = verify_ssl_payment(val_id, amount)
    if not verified and status == 'VALID':
        return Response({'status': 'INVALID_TRANSACTION'}, status=400)

    if status in ('VALID', 'VALIDATED'):
        commission, hospital_payout = calculate_commission(amount)
        hospital_admin_id = data.get('value_c', '')
        booking_ref       = data.get('value_d', tran_id)

        # Record commission
        _record_commission(
            tran_id=tran_id,
            total_amount=amount,
            commission=commission,
            hospital_payout=hospital_payout,
            hospital_admin_id=hospital_admin_id,
            booking_ref=booking_ref,
        )

        # Mark booking as paid
        _confirm_booking(booking_ref)

        return Response({'status': 'OK', 'tran_id': tran_id})

    return Response({'status': 'FAILED'})


def verify_ssl_payment(val_id: str, amount: Decimal) -> bool:
    """Verify payment with SSLCommerz validation API"""
    try:
        resp = requests.get(
            f"{get_ssl_base()}/validator/api/validationserverAPI.php",
            params={
                'val_id': val_id,
                'store_id': getattr(settings, 'SSLCOMMERZ_STORE_ID', 'testbox'),
                'store_passwd': getattr(settings, 'SSLCOMMERZ_STORE_PASSWD', 'qwerty'),
                'format': 'json',
            },
            timeout=15,
        )
        result = resp.json()
        if result.get('status') in ('VALID', 'VALIDATED'):
            server_amount = Decimal(str(result.get('amount', 0)))
            return abs(server_amount - amount) < Decimal('1.00')  # allow ৳1 tolerance
    except Exception:
        pass
    return False  # In demo/offline mode, bypass verification


def _record_commission(tran_id, total_amount, commission, hospital_payout, hospital_admin_id, booking_ref):
    """
    Record commission split in database.
    5%  → Super Admin (Ahsanul Yamin, bKash: 01772172829)
    95% → Hospital Admin
    """
    try:
        from apps.monetization.models import CommissionRecord
        CommissionRecord.objects.update_or_create(
            tran_id=tran_id,
            defaults={
                'total_amount': total_amount,
                'super_admin_commission': commission,
                'super_admin_pct': float(SUPER_ADMIN_PCT),
                'super_admin_bkash': SUPER_ADMIN_BKASH,
                'super_admin_nagad': SUPER_ADMIN_NAGAD,
                'hospital_payout': hospital_payout,
                'hospital_admin_id': hospital_admin_id,
                'booking_ref': booking_ref,
                'status': 'collected',
                'paid_at': datetime.now(),
            }
        )
    except Exception:
        pass  # Log in production


def _confirm_booking(booking_ref: str):
    """Mark booking as confirmed after successful payment"""
    try:
        from apps.appointments.models import Appointment
        Appointment.objects.filter(booking_ref=booking_ref, status='pending_payment').update(
            status='confirmed', payment_status='paid'
        )
    except Exception:
        pass


# ── SUCCESS / FAIL / CANCEL VIEWS ─────────────────────────────────────────────
@csrf_exempt
def payment_success(request):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id', '')
    return HttpResponseRedirect(f'/pages/payment/success.html?tran_id={tran_id}')


@csrf_exempt
def payment_fail(request):
    return HttpResponseRedirect('/pages/payment/fail.html')


@csrf_exempt
def payment_cancel(request):
    return HttpResponseRedirect('/pages/payment/cancel.html')


# ── ADMIN: COMMISSION SUMMARY ──────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commission_summary(request):
    """
    GET /api/v1/payments/commission-summary/
    Super Admin only — view total commissions earned.
    """
    if not request.user.is_staff:
        return Response({'error': 'Super Admin only'}, status=403)

    try:
        from apps.monetization.models import CommissionRecord
        from django.db.models import Sum, Count
        qs = CommissionRecord.objects.filter(status='collected')
        total = qs.aggregate(
            total_commission=Sum('super_admin_commission'),
            total_transactions=Count('id'),
            total_gross=Sum('total_amount'),
        )
        return Response({
            'super_admin_bkash': SUPER_ADMIN_BKASH,
            'super_admin_nagad': SUPER_ADMIN_NAGAD,
            'commission_pct': float(SUPER_ADMIN_PCT),
            'total_commission_earned': str(total['total_commission'] or 0),
            'total_transactions': total['total_transactions'],
            'total_gross_processed': str(total['total_gross'] or 0),
        })
    except Exception as e:
        # Demo data when DB not yet set up
        return Response({
            'super_admin_bkash': SUPER_ADMIN_BKASH,
            'super_admin_nagad': SUPER_ADMIN_NAGAD,
            'commission_pct': 5,
            'total_commission_earned': '48000.00',
            'total_transactions': 840,
            'total_gross_processed': '960000.00',
            'note': 'Demo data — configure database to see live data',
        })
