import base64

##############################################################################
# base class for building packages
##############################################################################
class DbPackage(object):

    def installPackage(self, dbCon):
        self.installPrerequisites(dbCon)
        self.installHeader(dbCon)
        self.installBody(dbCon)
        self.installPostrequisites(dbCon)

    def installPrerequisites(self, dbCon):
        try:
            script = base64.b64decode(self._pkgPrerequisites)
            self._executeScript(dbCon, script)
        except AttributeError:
            pass

    def installHeader(self, dbCon):
        script = base64.b64decode(self._pkgHeader)
        self._executeScript(dbCon, script)

    def installBody(self, dbCon):
        script = base64.b64decode(self._pkgBody)
        self._executeScript(dbCon, script)

    def installPostrequisites(self, dbCon):
        try:
            script = base64.b64decode(self._pkgPostrequisites)
            self._executeScript(dbCon, script)
        except AttributeError:
            pass


#--------------------------
# database utilities
#--------------------------
    def _executeScript(self, dbCon, script):
        cur = dbCon.cursor()
        cur.execute(script)
        return cur.rowcount

