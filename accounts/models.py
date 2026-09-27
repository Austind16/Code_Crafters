from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='student_profile',
	)
	name = models.CharField(max_length=150)
	division = models.CharField(max_length=10)
	division_roll_number = models.CharField(max_length=20)
	branch = models.CharField(max_length=100)
	enrollment_number = models.CharField(max_length=50, unique=True)
	semester = models.SmallIntegerField(null=True, blank=True)


class AdminProfile(models.Model):
	STAFF_TYPES = (
		('faculty', 'Faculty'),
		('supervisor', 'Supervisor'),
		('superuser', 'Superuser'),
	)

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='admin_profile',
	)
	name = models.CharField(max_length=150)
	staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
