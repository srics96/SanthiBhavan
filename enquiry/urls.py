from django.conf.urls import include
from django.conf.urls import url

from tastypie.api import Api

from enquiry.api import EnquiryResource
from enquiry.views import success, failure, render_booknow, render_admin, render_aboutus, render_home, render_whyus, render_contactus, render_gallery

v1_api = Api(api_name='v1')
v1_api.register(EnquiryResource())


urlpatterns = [
	url(r'^success', success, name='success'),
	url(r'^failure', failure, name='failure'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^whyus', render_whyus, name='render_whyus'),
    url(r'^booknow', render_booknow, name='render_booknow'),
    url(r'^contactus', render_contactus, name='render_contactus'),
    url(r'^gallery', render_gallery, name='render_gallery'),
    url(r'^admin/', render_admin, name='render_admin'),
    url(r'^aboutus', render_aboutus, name='render_aboutus'),
    url(r'^', render_home, name="render_home"),
]