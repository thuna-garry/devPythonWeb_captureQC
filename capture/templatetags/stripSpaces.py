"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from django import template

register = template.Library()

# code taken from:  http://www.djangotips.com/strip-all-white-spaces-template-tag

class StripspacesNode(template.base.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        s = self.nodelist.render(context).strip()
        s = re.sub(r'\s+', ' ', s)
        s = re.sub(r'/\*+\*/', '/**/', s)
        return s

@register.tag
def stripspaces(parser, token):
    nodelist = parser.parse(('endstripspaces',))
    parser.delete_first_token()
    return StripspacesNode(nodelist)
