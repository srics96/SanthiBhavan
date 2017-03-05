from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage

from ast import literal_eval
from celery.result import AsyncResult


from django.conf import settings

from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from datetime import datetime

from enquiry.models import Enquiry, Payment, PersonalData, Reservation
from enquiry.tasks import dispatch_email, send_invoice
from enquiry import utils

from forms import PayUForm, HashForm, OrderForm
from utils import verify_hash, generate_hash

import _constants
import dateutil.parser
import requests
import base64
import json
import smtplib

from uuid import uuid4
from random import randint
import logging

logger = logging.getLogger('django')

invoice_dict = {}


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def send_email_to_customer(enquiry_object):
    current_time = datetime.now().time()
    if current_time.hour >= _constants.NON_WORKING_TIME_START or current_time.hour <= _constants.NON_WORKING_TIME_END:
        message = 'Hey {0}, \n Thanks for expressing your interest. Sorry, We are currently offline. Our Customer Facilitation team is available from 8am to 6pm. \n We will contact you shortly. \n \n Regards Hotel Shanthi Bhavan'.format(enquiry_object.name)
    else:
        message = 'Hey {0}, \n Thanks for expressing your interest. Our Customer Facilitation team will contact you shortly.\n \n Regards Hotel Santhi Bhavan'.format(enquiry_object.name)
    
    subject = "We've received your message"
    recipient = enquiry_object.email
    dispatch_email.delay(subject, message, recipient)


def send_email_to_manager(enquiry_object_id):
    enquiry_object = Enquiry.objects.get(id=enquiry_object_id)
    subject = 'Enquiry from {}'.format(enquiry_object.name)
    if enquiry_object.mobile_number:
        mobile_optional_string = 'Mobile - {0} \n'.format(enquiry_object.mobile_number)
    else:   
        mobile_optional_string = ''
    message = '{0} \n Email - {1} \n {2} \n \n Regards KlickKit Web Team'.format(enquiry_object.message, enquiry_object.email, mobile_optional_string)
    recipient = _constants.MANAGER_MAIL
    dispatch_email.delay(subject, message, recipient)


def render_aboutus(request):
    if request.method == 'GET': 
        return render(request, 'enquiry/aboutus.html')
        

def render_response(request):
    if request.method == 'GET': 
        return render(request, 'enquiry/response.html')

def render_admin(request):
    if request.method == 'GET':
        return render(request, 'enquiry/hotel_admin.html')
    if request.method == 'POST':
        received_json_data=json.loads(request.body)
        json_data = byteify(received_json_data)
        json_data = dict(json_data)
        date = json_data.get('date')
        name = json_data.get('name')
        availability_and_discount = json_data.get('availability_and_discount')
        for key, value in availability_and_discount.items():
            if key == 'discount':
                discount = value
            else:
                availability = value
        return HttpResponse("OK")


def render_home(request):
    if request.method == 'GET':
       return render(request, 'enquiry/index.html')
       
    if request.method == 'POST':
        
        now = str(datetime.now().date())
        name = request.POST['firstname']
        email = request.POST['email']
        phone = int(request.POST['phone'])
        number_of_adults = int(request.POST['numberOfAdults'])
        number_of_children = int(request.POST['numberOfChildren'])
        number_of_rooms = int(request.POST['numberOfRooms'])
        checkin_date = dateutil.parser.parse(request.POST['checkindatetime']).date()
        checkout_date = dateutil.parser.parse(request.POST['checkoutdatetime']).date()
        room_type = request.POST['selectedRoom']
        total_amount = int(request.POST['totalAmount'])
        number_of_days = int(request.POST['noOfDays'])
        txnid = uuid4().hex

        personal_data = PersonalData(name=name, email=email, phone=phone, number_of_adults=number_of_adults, 
                                     number_of_children=number_of_children)
        personal_data.save()

        reservation_data = Reservation(name=name, phone=phone, email=email, number_of_rooms=number_of_rooms,
                                       checkin_date=checkin_date, checkout_date=checkout_date, room_type=room_type,
                                       txnid=txnid, number_of_days=number_of_days, total_amount=total_amount)
        reservation_data.save()
        # PayU Essential parameters 
        dict_key = {}
        keys = ('firstname', 'phone', 'email')
        for key in keys:
            dict_key[key] = request.POST[key]
        initial = {'txnid': txnid,
                    'productinfo': '123',
                    'amount': randint(100, 1000)/100.0
        }
        initial.update(dict_key)
        initial.update({
            'key': settings.PAYU_INFO['merchant_key'],
            'surl': request.build_absolute_uri(reverse('success')),
            'furl': request.build_absolute_uri(reverse('failure')),
            'curl': request.build_absolute_uri(reverse('failure'))
        })
        payu_form = PayUForm(initial)
        if payu_form.is_valid():
            context = {'form': payu_form,
                        'hash_form':HashForm({'hash':generate_hash(payu_form.cleaned_data)}),
                        'action': "%s" % settings.PAYU_INFO['payment_url']}
            return render(request, 'enquiry/payu_form.html', context)
        else:
            logger.error('Something went wrong! Looks like initial data\
                        used for payu_form is failing validation')
            return HttpResponse(status=500)
        
        
@csrf_exempt
def success(request):
    if request.method == 'POST':
        if not verify_hash(request.POST):
            logger.warning("Response data for order (txnid: %s) has been "
                           "tampered. Confirm payment with PayU." %
                           request.POST.get('txnid'))
            return redirect('failure')
        else:
            invoice_dict = {}
            logger.warning("Payment for order (txnid: %s) succeeded at PayU" %
                           request.POST.get('txnid'))
            reservation_data = Reservation.objects.get(txnid=request.POST['txnid'])
            payment = Payment(booking=reservation_data)
            payment.save()
            invoice_dict['firstname'] = reservation_data.name
            invoice_dict['numberOfRooms'] = reservation_data.number_of_rooms
            invoice_dict['noOfDays'] = reservation_data.number_of_days
            invoice_dict['email'] = reservation_data.email
            invoice_dict['phone'] = reservation_data.phone
            invoice_dict['selectedRoom'] = reservation_data.room_type
            invoice_dict['totalAmount'] = reservation_data.total_amount
            invoice_dict['txnid'] = request.POST['txnid']
            invoice_dict['date'] = str(datetime.now().date())
            ctx = {'invoice_dict' : invoice_dict}
            message = get_template('enquiry/receipt.html').render(Context(ctx))
            send_invoice.delay(invoice_dict, message)
            return render(request, 'enquiry/transuccess.html', {'txnid' : request.POST['txnid']})
    else:
        raise Http404

@csrf_exempt
def failure(request):
    if request.method == 'POST':
        return render(request, 'enquiry/transfail.html', {'txnid' : request.POST['txnid']} )
    else:
        raise Http404


def render_whyus(request):
    if request.method == 'GET':
        return render(request, 'enquiry/whyus.html')


def render_gallery(request):
    if request.method == 'GET':
        return render(request, 'enquiry/gallery.html')
        

def render_contactus(request):
    if request.method == 'GET':
        return render(request, 'enquiry/contactus.html')
    elif request.method == 'POST':
        name = request.POST['name']
        mobile_number = request.POST['phone']
        email = request.POST['email']
        message = request.POST['message']
        enquiry_obj = Enquiry(name=name, email=email, message=message)
        if mobile_number:
            if utils.validate_international_phone_number(mobile_number):
                enquiry_obj.mobile_number = mobile_number
        enquiry_obj.save()
        id = enquiry_obj.id
        task_id = send_email_to_manager(id)
        send_email_to_customer(enquiry_obj)
        didSendEmail = 'true'
        return render(request, 'enquiry/contactus.html', dict(didSendEmail=didSendEmail))

def render_booknow(request):
    if request.method == 'GET':
        return render(request, 'enquiry/booknow.html')
    
        




