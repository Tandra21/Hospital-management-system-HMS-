# Generated migration for donate app
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DonorRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donor_id', models.CharField(db_index=True, max_length=32, unique=True)),
                ('name', models.CharField(max_length=120)),
                ('dob', models.DateField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('nid', models.CharField(max_length=30)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.TextField()),
                ('blood_group', models.CharField(max_length=5)),
                ('organs', models.JSONField(default=list)),
                ('conditions', models.TextField(blank=True)),
                ('medications', models.TextField(blank=True)),
                ('ec_name', models.CharField(max_length=120)),
                ('ec_relation', models.CharField(max_length=40)),
                ('ec_phone', models.CharField(max_length=20)),
                ('family_informed', models.CharField(choices=[('yes', 'Yes'), ('no', 'Not yet'), ('partial', 'Partial')], default='no', max_length=10)),
                ('note', models.TextField(blank=True)),
                ('lang', models.CharField(default='en', max_length=5)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('registered_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-registered_at'],
            },
        ),
        migrations.CreateModel(
            name='AwarenessContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('lang', models.CharField(choices=[('en', 'English'), ('bn', 'Bengali')], default='en', max_length=5)),
                ('category', models.CharField(default='general', max_length=60)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='DonorWithdrawal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(blank=True)),
                ('withdrawn_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donate.donorregistration')),
            ],
        ),
    ]
