"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import os
import json
import logging

from django.shortcuts                    import render
from django.core.urlresolvers            import reverse
from django.http                         import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.sessions.backends.db import SessionStore
from django.core.servers.basehttp        import FileWrapper


#############################################################################
# utility
#############################################################################
def jsonDump(obj, comment=""):
    if comment:
        comment += " "
    if isinstance(obj, SessionStore):
        obj = dict(obj.items())
    return comment + json.dumps(obj, sort_keys=True, indent=4, separators=(', ', ': '))


#############################################################################
# python decorators
#############################################################################
def viewSecurity(revString, admin=False):
    def wrap(f):
        def wrapped_f(request, *args, **kwargs):
            if request.session.get('conUser', ""):  #are they logged in
                if admin and not request.session['conUser']['admin']:
                    return HttpResponse(status=403)
                else:
                    return f(request, *args, **kwargs)
            else:
                request.session.set_test_cookie()
                request.session['interceptedUri'] = (revString, args, kwargs)
                return HttpResponseRedirect( reverse('capture:sessionErr') )
        return wrapped_f
    return wrap

def ajaxSecurity(f):
    def wrapped_f(request, *args, **kwargs):
        if request.session.get('conUser', ""):
            return f(request, *args, **kwargs)
        else:
            return dict()
    return wrapped_f


#############################################################################
# json responses
#############################################################################
def jsonResponse(resp):
    return HttpResponse(json.dumps(resp,separators=(',',':')), content_type='application/json')

def emptyJsonResponse():
    return HttpResponse(json.dumps(dict(),separators=(',',':')), content_type='application/json')

def jsonErrorResponse(payload, httpReason):
    return HttpResponse(json.dumps(payload, separators=(',',':')), content_type='application/json', status=500, reason=httpReason)

def jsonRedirect(payload, httpReason):
    # a cludge:  a 303 should really use the http 'location:' header but were piggybacking on the mechanism
    # used in our controllers for errors.  Why? because this avoids the browser from seeing an error response
    return HttpResponse(json.dumps(payload, separators=(',',':')), content_type='application/json', status=303, reason=httpReason)


#############################################################################
# named exceptions
#############################################################################
class SessionError(Exception):
    pass


#############################################################################
# nav utility
#############################################################################
def navStackModify(session, label, href):
    stack = session.get('navStack', [])
    curIdx = -1
    labelIdx = -1
    for entry in stack:
        curIdx += 1
        if entry['label'] == label:
            labelIdx = curIdx
            break
    if labelIdx == -1:  # not found in stack
        stack.append(dict(label=label, href=href))
    else:
        stack = stack[:labelIdx+1]
    session['navStack'] = stack

def navStackParent(session):
    stack = session.get('navStack', [])
    if len(stack) > 1:
        return stack[-2]['href']
    else:
        return reverse('capture:login')


