import json

from django.conf.urls import url

from tastypie.constants import ALL
from tastypie.http import HttpNotFound
from tastypie.resources import ModelResource
from tastypie.resources import Resource
from tastypie.utils.urls import trailing_slash


from enquiry.models import Enquiry


class EnquiryResource(ModelResource):
    class Meta:
        queryset = Enquiry.objects.all()
        resource_name = 'enquiry'
        allowed_methods = ['get', 'post']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/update%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('save_admin_updates'), name="api_save_admin_updates"),
        ]

    def save_admin_updates(self, request, *args, **kwargs):
        try:
            room_types = json.loads(request.body).get('room_types')
            print room_types
            return self.create_response(request, dict(
                status=True,
                message='Update commited ro database',
            ))
        except KeyError, key_err:
            return self.error_response(request, dict(
                API_ERROR_CODE='keyError',
                API_ERROR_MESSAGE=key_err.message,
            ))
        
        



