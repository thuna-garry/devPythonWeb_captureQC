"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import root.config  #ensure that config runs before settings - even in IDE
from aqclib import utils

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# setup logging globally
import logging
logging.basicConfig(level=logging.WARNING)

# SECURITY WARNING: keep the secret key used in production secret!
# import random
# print ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
SECRET_KEY = 'ot@gd(bg8_hku)c*((365-b-ao7fwkc6m)q)#_-jao07es$*dp'

# SECURITY WARNING: don't run with debug turned on in production!
#utils.setDebugEnabled(False)
DEBUG          = utils.debugEnabled()
TEMPLATE_DEBUG = utils.debugEnabled()
ALLOWED_HOSTS = ['*',]

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'capture',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'root.urls'
WSGI_APPLICATION = 'root.wsgi.application'


# sessions
#SESSION_EXPIRE_AT_BROWSER_CLOSE
SESSION_COOKIE_AGE = 8 * 3600
SESSION_COOKIE_NAME = "sessionid_" + utils.globalDict['application.name']
sessionMsg = "Using database sessions."
if utils.globalDict.get('redisSock'):
    import stat
    try:
        mode = os.stat(utils.globalDict['redisSock']).st_mode
        if stat.S_ISSOCK(mode):
            sessionMsg = "Using redis sessions."
            SESSION_ENGINE = 'redis_sessions.session'
            SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = utils.globalDict['redisSock']
    except:
        pass
logging.debug(sessionMsg)


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'root', 'db.sqlite3'),
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticFiles")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "root",    "static"),
    os.path.join(BASE_DIR, "capture", "static"),            #question: same as below how would name clashes be handled when apps want to use
    #os.path.join(BASE_DIR, "customerPortal", "static"),    #          generic names for static resources  (eg. "mainPageLogo.png")
                                                            #answer: don't put files directly into the "static" directory, but add
                                                            #        another directory level named after the app; for example
                                                            #        files for      os.path.join(BASE_DIR, "root", "static")
                                                            #        should go into   BASE_DIR/root/static/root/  and the django tag
                                                            #        would be {% static root/<filename> %}
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
utils.globalDict["path.mediaRoot"] = os.path.abspath(MEDIA_ROOT)
utils.globalDict["mediaURL"] = MEDIA_URL

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'root.config.rootContext',
    'capture.config.localContext',
    # All context processors are called for each request.  So if we have a number of django applications, and each
    # needs to create context entries that are application specific but named generically (eg {{APP_NAME}} )
    # then the context processor must deduce from its request object whether or not it is being called for
    # it's local/intended app, before populating/returning the context.
)

