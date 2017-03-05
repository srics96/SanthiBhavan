from django.db import models
from django.utils import timezone

from datetime import datetime, timedelta

class Enquiry(models.Model):
    name = models.CharField(max_length=20, null=False)
    email = models.CharField(max_length=30, null=False)
    mobile_number = models.IntegerField(default=None, null=True)
    message = models.CharField(max_length=1000, null=False)

class PersonalData(models.Model):
    name = models.CharField(max_length=20, null=False)
    email = models.CharField(max_length=30, null=False)
    phone = models.IntegerField(default=None, null=True)
    number_of_adults = models.IntegerField(default=1, null=False)
    number_of_children = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    PREMIUM_SINGLE = 'Premium Single'
    PREMIUM_DOUBLE = 'Premium Double'
    DELUXE_DOUBLE = 'Deluxe Double'

    TYPES = (
        (PREMIUM_SINGLE, 'Premium Single'),
        (PREMIUM_DOUBLE, 'Premium Double'),
        (DELUXE_DOUBLE, 'Deluxe Double'),
    )


    name = models.CharField(max_length=20, null=False)
    email = models.CharField(max_length=30, null=False, default=None)
    phone = models.IntegerField(default=None, null=True)
    number_of_rooms = models.IntegerField(default=1, null=False)
    checkin_date = models.DateField(default=datetime.now().date())
    checkout_date = models.DateField(default=( datetime.now().date() + timedelta(days=1)) )
    room_type = models.CharField(max_length=2, choices=TYPES, default=PREMIUM_SINGLE)
    number_of_days = models.IntegerField(default=0, null=False)
    txnid = models.CharField(max_length=30, default=None, null=True)
    total_amount = models.IntegerField(default=0, null=False)


class Payment(models.Model):
    booking = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    


        


