# donate/models.py
from django.db import models
from django.utils import timezone
import uuid


class DonorRegistration(models.Model):
    GENDER_CHOICES = [('male','Male'),('female','Female'),('other','Other')]
    FAMILY_CHOICES = [('yes','Yes'),('no','Not yet'),('partial','Partial')]

    donor_id        = models.CharField(max_length=32, unique=True, db_index=True)
    name            = models.CharField(max_length=120)
    dob             = models.DateField()
    gender          = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nid             = models.CharField(max_length=30)
    phone           = models.CharField(max_length=20)
    email           = models.EmailField(blank=True)
    address         = models.TextField()
    blood_group     = models.CharField(max_length=5)
    organs          = models.JSONField(default=list)
    conditions      = models.TextField(blank=True)
    medications     = models.TextField(blank=True)

    ec_name         = models.CharField(max_length=120)
    ec_relation     = models.CharField(max_length=40)
    ec_phone        = models.CharField(max_length=20)
    family_informed = models.CharField(max_length=10, choices=FAMILY_CHOICES, default='no')
    note            = models.TextField(blank=True)

    lang            = models.CharField(max_length=5, default='en')
    is_active       = models.BooleanField(default=True)
    is_verified     = models.BooleanField(default=False)
    registered_at   = models.DateTimeField(default=timezone.now)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'donate'
        ordering  = ['-registered_at']

    def save(self, *args, **kwargs):
        if not self.donor_id:
            year = timezone.now().year
            uid  = str(uuid.uuid4()).replace('-','').upper()[:6]
            self.donor_id = f'MF-{year}-{uid}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.donor_id} — {self.name} ({self.blood_group})'


class AwarenessContent(models.Model):
    LANG_CHOICES = [('en','English'),('bn','Bengali')]
    title    = models.CharField(max_length=200)
    body     = models.TextField()
    lang     = models.CharField(max_length=5, choices=LANG_CHOICES, default='en')
    category = models.CharField(max_length=60, default='general')
    active   = models.BooleanField(default=True)
    created  = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'donate'

    def __str__(self):
        return f'[{self.lang}] {self.title}'


class DonorWithdrawal(models.Model):
    donor    = models.ForeignKey(DonorRegistration, on_delete=models.CASCADE)
    reason   = models.TextField(blank=True)
    withdrawn_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'donate'
