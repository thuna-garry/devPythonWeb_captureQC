"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import os
import sys
import logging

from aqclib import utils
from aqclib import dbUtils


########################################################################################
# global environment
########################################################################################
utils.globalDict['application.displayName'] = 'AdvanceQC CaptuerQC'
utils.globalDict['application.name']        = 'CaptureQC'         #change will invalidate existing licenses
utils.globalDict['application.version']     = '2015.04.06'
utils.globalDict['copyright']   = "Copyright AdvanceQC LLC 2014,2015.  All rights reserved"

utils.globalDict['path.root'] = os.path.abspath( os.path.dirname(__file__) )
utils.globalDict['path.base'] = os.path.dirname( utils.globalDict['path.root'] )
utils.globalDict['path.version'] = os.path.join( utils.globalDict['path.root'], 'version.{}.aqc'.format(utils.globalDict['application.name']))

if __name__ == "__main__":
    if '-version' in sys.argv:
        fname = utils.globalDict['path.version']
        print "Writing version in licensing format to: {}".format(fname)
        with open(fname, 'wb') as f:
            f.write(utils.pickleEncode({'application.displayName' : utils.globalDict['application.displayName'],
                                        'application.name'        : utils.globalDict['application.name'],
                                        'application.version'     : utils.globalDict['application.version'], })
                   )
        print "Done."
        sys.exit()


########################################################################################
# global environment
########################################################################################
utils.configInit(None)

# read config items from the local database
import sqlite3
dbf = os.path.join(utils.globalDict['path.root'], 'db.sqlite3')
con = sqlite3.connect(dbf)
cur = con.cursor()
cur.execute("select * from capture_aqcConfig where appName = ?", (utils.globalDict['application.name'],) )
rec = dict(zip([col[0] for col in cur.description], cur.fetchone()))
utils.globalDict.update(rec)
con.close()


# do we set debug_ mode on
utils.setDebugEnabled( utils.globalDict['trace'] == "AdvanceQC" )
if utils.debugEnabled():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler(sys.stderr)
    # handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)


# set up the database pool
dbUtils.dbInit()


def rootContext(request):
    return { k.upper():v for k,v in utils.globalDict.iteritems() }
