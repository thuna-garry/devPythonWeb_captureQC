"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

from capture import viewsCore
from capture import viewsSession
from capture import viewsUser
from capture.viewsCapture                 import ViewCapture
from capture.viewsCaptureAttendance       import ViewCaptureAttendance
from capture.viewsCaptureLabour           import ViewCaptureLabour
from capture.viewsCaptureLabourBatch      import ViewCaptureLabourBatch
from capture.viewsCaptureWorkOrderStatus  import ViewCaptureWorkOrderStatus
from capture.viewsCaptureStockDemand      import ViewCaptureStockDemand
from capture.viewsCaptureStockIssue       import ViewCaptureStockIssue
from capture.viewsCaptureStockUndo        import ViewCaptureStockUndo
from capture.viewsCaptureStockSearch      import ViewCaptureStockSearch
from capture.viewsCaptureStockTurnIn      import ViewCaptureStockTurnIn
from capture.viewsCaptureStockLabel       import ViewCaptureStockLabel

urlpatterns = patterns('',

    #session
    url(r'^$',                               viewsSession.welcome,        name='welcome'),
    url(r'^login/$',                         viewsSession.login,          name='login'),
    url(r'^logout/$',                        viewsSession.logout,         name='logout'),
    url(r'^userAgreement/$',                 viewsSession.userAgreement,  name='userAgreement'),
    url(r'^resetPassword/$',                 viewsSession.resetPassword,  name='resetPassword'),
    url(r'^menu/$',                          viewsSession.menu,           name='menu'),
    url(r'^about/$',                         viewsSession.about,          name='about'),
    url(r'^sessionErr/$',                    viewsSession.sessionErr,     name='sessionErr'),

    #capture
    url(r'^form/$',                                                               ViewCapture.as_view(),  name="ajax_formURL"),   #placeHolder for base reverse address
    url(r'^form/(?P<frmName>timeClock)(?:\.html)?(?:/(?P<target>\w+))?/?$',       ViewCaptureAttendance.as_view() ),
    url(r'^form/(?P<frmName>labour)(?:\.html)?(?:/(?P<target>\w+))?/?$',          ViewCaptureLabour.as_view() ),
    url(r'^form/(?P<frmName>labourBatch)(?:\.html)?(?:/(?P<target>\w+))?/?$',     ViewCaptureLabourBatch.as_view() ),
    url(r'^form/(?P<frmName>woStatus)(?:\.html)?(?:/(?P<target>\w+))?/?$',        ViewCaptureWorkOrderStatus.as_view() ),
    url(r'^form/(?P<frmName>stockIssue)(?:\.html)?(?:/(?P<target>\w+))?/?$',      ViewCaptureStockIssue.as_view() ),
    url(r'^form/(?P<frmName>stockDemand)(?:\.html)?(?:/(?P<target>\w+))?/?$',     ViewCaptureStockDemand.as_view() ),
    url(r'^form/(?P<frmName>stockUndo)(?:\.html)?(?:/(?P<target>\w+))?/?$',       ViewCaptureStockUndo.as_view() ),
    url(r'^form/(?P<frmName>stockSearch)(?:\.html)?(?:/(?P<target>\w+))?/?$',     ViewCaptureStockSearch.as_view() ),
    url(r'^form/(?P<frmName>stockTurnIn)(?:\.html)?(?:/(?P<target>\w+))?/?$',     ViewCaptureStockTurnIn.as_view() ),
    url(r'^form/(?P<frmName>stockLabel)(?:\.html)?(?:/(?P<target>\w+))?/?$',      ViewCaptureStockLabel.as_view(),  name="stockLabel"),

    #users
    url(r'^profile/$',                       viewsUser.profile,           name='profile'),

    #core
    url(r'^version/$',                       viewsCore.version,           name='version'),
    url(r'^systemErr/$',                     viewsCore.systemErr,         name='systemErr'),
    url(r'^(?P<url>.*)/$',                   viewsCore.catchAll,          name='catchAll'),
)


