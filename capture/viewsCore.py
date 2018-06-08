"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import os
import logging

from django.core.servers.basehttp     import FileWrapper
from django.http                      import HttpResponse, HttpResponseNotFound
from django.shortcuts                 import render

from aqclib import utils


#############################################################################
# basic scaffolding views -- might not even require any templates
#############################################################################
def version(request):
    """ provide view for version file """
    fname = utils.globalDict['path.version']
    response = HttpResponse(FileWrapper(open(fname, 'r')), content_type='application/aqc')
    response['Content-Disposition'] = 'attachment; filename=CaptureQC.ver'
    return response

def systemErr(request):
    """ diaply last systemError stashed in the session prior to being redirected here """
    msg=""; msgDetail=""
    try:
        msg, traceback = request.session['systemError']
        del request.session['systemError']
        request.session.modified = True
    except:
        pass
    return render(request, 'core/systemErr.html', dict(msg=msg, msgDetail=msgDetail))

def catchAll(request, url):
    """ provide view for unmatched URL """
    logging.debug("catchAll url: " + url)
    return HttpResponseNotFound('<h1>Catch All</h1><code>{0}</code>'.format(url))

