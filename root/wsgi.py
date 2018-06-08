"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved

WSGI config for CaptureQC project.
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

import root.config

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
