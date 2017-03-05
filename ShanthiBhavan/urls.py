from django.contrib import admin
from django.conf.urls import include
from django.conf.urls import url


urlpatterns = [
	url(r'^isapianist/', admin.site.urls),
    url(r'^', include("enquiry.urls")),
    
]
