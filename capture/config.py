"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

#from django.conf import settings
contextItems = dict(
    # css constants
    PAGE_HEADER_HEIGHT = 60,
    CLIENT_AREA_HEIGHT_USED = 238,
    GRID_VERT_SCROLLBAR_WIDTH = 17,   #used to prevent horizontal scrollbar from displaying
)

def localContext(request):
    return contextItems
