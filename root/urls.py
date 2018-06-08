"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

from django.conf import settings
#print settings.TEMPLATE_CONTEXT_PROCESSORS

urlpatterns = patterns('',
    url(r'^$',                   include('capture.urls')),
    url(r'^admin/',              include(admin.site.urls)),
    url(r'^capture/',            include('capture.urls',         namespace='capture')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^favicon.ico/?$',      RedirectView.as_view(url='/static/favicon/favicon.ico'), name='favicon'),
)

if not settings.DEBUG:
    additional_settings = patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,} ),
    )
    urlpatterns += additional_settings