# donate/admin.py
from django.contrib import admin
from .models import DonorRegistration, AwarenessContent, DonorWithdrawal


@admin.register(DonorRegistration)
class DonorAdmin(admin.ModelAdmin):
    list_display  = ['donor_id','name','blood_group','phone','family_informed',
                     'is_active','is_verified','registered_at']
    list_filter   = ['blood_group','gender','family_informed','is_active','is_verified']
    search_fields = ['donor_id','name','phone','nid']
    readonly_fields = ['donor_id','registered_at','updated_at']
    ordering      = ['-registered_at']

    fieldsets = (
        ('Donor Info',      {'fields':('donor_id','name','dob','gender','nid','phone','email','address')}),
        ('Donation Details',{'fields':('blood_group','organs','conditions','medications')}),
        ('Emergency Contact',{'fields':('ec_name','ec_relation','ec_phone','family_informed','note')}),
        ('Status',          {'fields':('lang','is_active','is_verified','registered_at','updated_at')}),
    )

    actions = ['mark_verified','mark_inactive']

    def mark_verified(self, request, qs):
        qs.update(is_verified=True)
        self.message_user(request, f'{qs.count()} donors marked as verified.')
    mark_verified.short_description = 'Mark selected donors as verified'

    def mark_inactive(self, request, qs):
        qs.update(is_active=False)
        self.message_user(request, f'{qs.count()} donors deactivated.')
    mark_inactive.short_description = 'Deactivate selected donors'


@admin.register(AwarenessContent)
class AwarenessAdmin(admin.ModelAdmin):
    list_display = ['title','lang','category','active','created']
    list_filter  = ['lang','category','active']


@admin.register(DonorWithdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['donor','reason','withdrawn_at']
    readonly_fields = ['withdrawn_at']
