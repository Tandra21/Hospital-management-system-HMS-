# donate/views.py
import json, logging
from django.http      import JsonResponse
from django.views     import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils     import timezone
from .models          import DonorRegistration, DonorWithdrawal

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class DonorRegisterView(View):
    """POST /api/donate/register/ — Register a new voluntary donor."""

    REQUIRED = ['name','dob','gender','nid','phone','address',
                'blood_group','organs','ec_name','ec_relation','ec_phone']

    def post(self, request):
        try:
            body = json.loads(request.body)

            # Validate required fields
            missing = [f for f in self.REQUIRED if not body.get(f)]
            if missing:
                return JsonResponse({'error': f'Missing fields: {", ".join(missing)}'}, status=400)

            # Check duplicate NID
            if DonorRegistration.objects.filter(nid=body['nid'], is_active=True).exists():
                return JsonResponse({'error': 'A registration with this NID already exists.'}, status=409)

            donor = DonorRegistration.objects.create(
                name            = body['name'].strip(),
                dob             = body['dob'],
                gender          = body.get('gender',''),
                nid             = body['nid'].strip(),
                phone           = body['phone'].strip(),
                email           = body.get('email','').strip(),
                address         = body['address'].strip(),
                blood_group     = body['blood_group'],
                organs          = body.get('organs', []),
                conditions      = body.get('conditions','').strip(),
                medications     = body.get('medications','').strip(),
                ec_name         = body['ec_name'].strip(),
                ec_relation     = body['ec_relation'],
                ec_phone        = body['ec_phone'].strip(),
                family_informed = body.get('family_informed','no'),
                note            = body.get('note','').strip(),
                lang            = body.get('lang','en'),
            )

            logger.info(f'New donor registered: {donor.donor_id} — {donor.name}')

            return JsonResponse({
                'status':   'success',
                'donor_id': donor.donor_id,
                'message':  'Registration successful. Thank you for your noble decision.',
                'registered_at': donor.registered_at.isoformat(),
            }, status=201)

        except Exception as e:
            logger.error(f'DonorRegisterView error: {e}', exc_info=True)
            return JsonResponse({'error': 'Registration failed. Please try again.'}, status=500)


class DonorLookupView(View):
    """GET /api/donate/lookup/?donor_id=MF-2026-XXXXX — Look up donor by ID."""

    def get(self, request):
        donor_id = request.GET.get('donor_id','').strip().upper()
        if not donor_id:
            return JsonResponse({'error': 'donor_id is required'}, status=400)
        try:
            d = DonorRegistration.objects.get(donor_id=donor_id, is_active=True)
            return JsonResponse({
                'donor_id':       d.donor_id,
                'name':           d.name,
                'blood_group':    d.blood_group,
                'organs':         d.organs,
                'family_informed':d.family_informed,
                'registered_at':  d.registered_at.isoformat(),
                'is_verified':    d.is_verified,
            })
        except DonorRegistration.DoesNotExist:
            return JsonResponse({'error': 'Donor ID not found or registration withdrawn.'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class DonorWithdrawView(View):
    """POST /api/donate/withdraw/ — Withdraw donor registration."""

    def post(self, request):
        try:
            body     = json.loads(request.body)
            donor_id = body.get('donor_id','').strip().upper()
            nid      = body.get('nid','').strip()
            reason   = body.get('reason','').strip()

            if not donor_id or not nid:
                return JsonResponse({'error': 'donor_id and nid are required'}, status=400)

            donor = DonorRegistration.objects.get(donor_id=donor_id, nid=nid, is_active=True)
            donor.is_active = False
            donor.save()

            DonorWithdrawal.objects.create(donor=donor, reason=reason)
            logger.info(f'Donor withdrew: {donor_id}')

            return JsonResponse({
                'status':  'withdrawn',
                'message': 'Your registration has been successfully withdrawn.',
            })

        except DonorRegistration.DoesNotExist:
            return JsonResponse({'error': 'Donor not found or credentials do not match.'}, status=404)
        except Exception as e:
            logger.error(f'DonorWithdrawView error: {e}', exc_info=True)
            return JsonResponse({'error': 'Withdrawal failed.'}, status=500)


class DonorStatsView(View):
    """GET /api/donate/stats/ — Public statistics."""

    def get(self, request):
        total       = DonorRegistration.objects.filter(is_active=True).count()
        blood_stats = {}
        for bg in ['A+','A-','B+','B-','AB+','AB-','O+','O-']:
            blood_stats[bg] = DonorRegistration.objects.filter(
                blood_group=bg, is_active=True).count()

        return JsonResponse({
            'total_donors': total,
            'blood_groups': blood_stats,
            'last_updated': timezone.now().isoformat(),
        })


class BloodDonorSearchView(View):
    """GET /api/donate/blood-search/ — Search blood donors by blood group & division."""

    def get(self, request):
        blood_group = request.GET.get('blood_group', '').strip()
        division    = request.GET.get('division', '').strip()
        district    = request.GET.get('district', '').strip()
        limit       = int(request.GET.get('limit', 20))

        qs = DonorRegistration.objects.filter(is_active=True)

        if blood_group:
            qs = qs.filter(blood_group=blood_group)
        if division:
            qs = qs.filter(address__icontains=division)
        if district:
            qs = qs.filter(address__icontains=district)

        qs = qs[:limit]

        donors = []
        for d in qs:
            initials = ''.join(p[0].upper() for p in d.name.split()[:2]) if d.name else '?'
            donors.append({
                'donor_id':      d.donor_id,
                'name':          d.name,
                'initials':      initials,
                'blood_group':   d.blood_group,
                'address':       d.address,
                'phone':         d.phone[:6] + 'XXXX' if len(d.phone) >= 10 else d.phone,
                'is_verified':   d.is_verified,
                'registered_at': d.registered_at.isoformat(),
            })

        return JsonResponse({'donors': donors, 'count': len(donors)})
