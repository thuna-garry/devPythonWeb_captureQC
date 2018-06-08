import logging

from aqclib import utils


#####################################################################################
# install routines
#####################################################################################
def install(dbCon):
    rc = installPackages(dbCon)
    if rc:
        return rc


def installPackages(dbCon):
    from capture.db.pkgAqcTrace  import AqcTrace
    from capture.db.pkgAqcCaptureQC import AqcCaptureQC
    pkgs = ['AqcTrace', 'AqcCaptureQC', 'Aqc_1952']

    for pkg in pkgs:
        logging.debug("""{pkg}().installPrerequisites(dbCon)""".format(pkg=pkg))
        rc = eval("""{pkg}().installPrerequisites(dbCon)""".format(pkg=pkg))
        if rc:
            return rc

    for pkg in pkgs:
        logging.debug("""{pkg}().installHeader(dbCon)""".format(pkg=pkg))
        rc = eval("""{pkg}().installHeader(dbCon)""".format(pkg=pkg))
        if rc:
            return rc

    for pkg in pkgs:
        logging.debug("""{pkg}().installBody(dbCon)""".format(pkg=pkg))
        rc = eval("""{pkg}().installBody(dbCon)""".format(pkg=pkg))
        if rc:
            return rc

    for pkg in pkgs:
        logging.debug("""{pkg}().installPostrequisites(dbCon)""".format(pkg=pkg))
        rc = eval("""{pkg}().installPostrequisites(dbCon)""".format(pkg=pkg))
        if rc:
            return rc
